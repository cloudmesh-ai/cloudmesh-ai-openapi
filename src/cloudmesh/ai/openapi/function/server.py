import os
import subprocess
import sys
import textwrap
from datetime import date
from importlib import import_module
from pathlib import Path
from typing import Optional, List, Dict, Any

import connexion
import yaml
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import path_expand
from cloudmesh.ai.openapi.registry.Registry import Registry


def dynamic_import(abs_module_path: str, class_name: str) -> Any:
    module_object = import_module(abs_module_path)
    target_class = getattr(module_object, class_name)
    return target_class


class Server(object):
    """
    This class manages all actions taken to interact with an OpenAPI AI server.
    """

    def __init__(self,
                 name: Optional[str] = None,
                 spec: Optional[str] = None,
                 directory: Optional[str] = None,
                 host: str = "127.0.0.1",
                 server: str = "flask",
                 port: int = 8080,
                 debug: bool = True):
        """
        Default constructor to initialize Server object

        :param name:  server name
        :param spec:  openapi spec yaml file
        :param directory:  directory for input file
        :param host:  host ip or dns name to be used to start service.  Default is 127.0.0.1
        :param server:  type of service to start.  Default is flask.
        :param port:  port to use for service.  Default is 8080. 
        :param debug:  flag to turn on debug logging.  Default is true.
        :return:  server object
        """

        if spec is None:
            Console.error("No service specification file defined")
            raise FileNotFoundError

        self.spec = path_expand(spec)

        self.name = Server.get_name(name, self.spec)

        if directory is None:
            self.directory = os.path.dirname(self.spec)
        else:
            self.directory = directory

        self.host = host or "127.0.0.1"
        self.port = port or 8080
        self.debug = debug or False
        self.server = server or "flask"
        self.server_command = ""

        data = dict(self.__dict__)
        #data['import'] = __name__

        VERBOSE(data, label="Server parameters")

        if server == "tornado":
            try:
                import tornado
            except Exception as e:
                print(e)
                Console.error(
                    "tornado not install. Please use `pip install tornado`")
                sys.exit(1)
                # return ""
            if self.debug:
                Console.error("Tornado does not support --verbose")
                sys.exit(1)
                # return ""

        Console.ok(self.directory)

    @staticmethod
    def get_name(name: Optional[str], spec: str) -> str:
        """
        Get the name of a server using specification

        :param name:  server name
        :param spec:  spec file name with fully qualified path
        :return:  server name
        """
        if name is None:
            return os.path.basename(spec).replace(".yaml", "")
        return name

    def _get_pid_file(self, name: str) -> Path:
        """
        Get the PID file path for a given server name.
        """
        return Path(self.directory) / f"{name}.pid"

    def _run_app(self) -> None:
        """
        Starts up a Connexion FastAPI app
        """
        Console.ok("starting server")

        sys.path.append(self.directory)
        # Use FastAPI backend for better concurrency
        app = connexion.App(__name__, 
                            specification_dir=self.directory,
                            backend="fastapi")

        app.add_api(self.spec)
        
        # Add health check endpoint
        @app.app.get("/health")
        async def health_check():
            return {"status": "healthy", "server": self.name}
        
        import uvicorn
        uvicorn.run(app, host=self.host, port=self.port, log_level="info" if self.debug else "warning")

    def _get_ai_metadata(self) -> Dict[str, Any]:
        """
        Extract AI metadata from config.yaml if available.
        """
        ai_metadata = {}
        try:
            config_path = Path(self.directory) / "config.yaml"
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                    if config and "llm" in config:
                        ai_metadata["ai_generated"] = True
                        ai_metadata["ai_model"] = config["llm"].get("model", "unknown")
        except (yaml.YAMLError, IOError) as e:
            Console.info(f"Could not load AI metadata from config: {e}")
        return ai_metadata

    def start(self, name: Optional[str] = None, spec: Optional[str] = None, foreground: bool = False) -> Optional[int]:
        """
        Start up an OpenApi server

        :param name:  server name
        :param spec:  openapi spec yaml file name
        :param foreground:  flag to run server in foreground.  Default is False.
        :return: started server PID
        """
        name = Server.get_name(name, spec)
        for active_server in Server.ps():
            if active_server['name'] == name and os.getpid() != active_server['pid']:
                Console.error(f'Server {name} already running on PID {active_server["pid"]}')
                return None

        if foreground:
            self._run_app()
            return None

        # Run as background process using subprocess
        # We create a temporary script to run the server, similar to run_os but cleaner
        pid = self.run_os()
        
        # The run_os method already handles registry registration and printing
        return pid

    @staticmethod
    def ps(name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all of the actively running servers using PID files.

        :param name:  Optional server name.
        :return:  list of running servers.
        """
        pids = []
        # Scan for .pid files in the current directory and subdirectories
        # In a real production environment, this would be a specific /var/run/cloudmesh directory
        for pid_file in Path(".").rglob("*.pid"):
            try:
                with open(pid_file, "r") as f:
                    pid = int(f.read().strip())
                
                # Verify if the process is actually running
                if Shell.is_pid_running(pid):
                    server_name = pid_file.stem
                    # We can't easily get the spec path from just the PID file 
                    # unless we store it there, so we'll look it up in the registry
                    registry = Registry()
                    entry = registry.list(name=server_name)
                    spec_path = entry[0]['spec'] if entry else "unknown"
                    
                    if name is None or name == server_name:
                        pids.append({"name": server_name, "pid": pid, "spec": spec_path})
            except (ValueError, IOError, IndexError):
                continue
        
        # Fallback to Shell.ps() if no PID files found or to complement them
        if not pids:
            result = Shell.ps()
            for pinfo in result:
                if pinfo["cmdline"]:
                    line = ' '.join(pinfo["cmdline"])
                    if "openapi server start" in line:
                        try:
                            parts = line.split("start")
                            spec_path = parts[1].split("--")[0].strip()
                            server_name = os.path.basename(spec_path).replace(".yaml", "")
                            if name is None or name == server_name:
                                pids.append({"name": server_name, "pid": pinfo['pid'], "spec": spec_path})
                        except (IndexError, ValueError):
                            continue
        return pids

    @staticmethod
    def list(name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists the servers that have been registered in Registry

        :param name:  Optional server name.
        :return:  list of servers in registry
        """
        registry = Registry()
        return registry.list(name)

    @staticmethod
    def stop(name: Optional[str] = None) -> None:
        """
        Stop a running OpenApi server

        :param name:  server name
        """
        if not name:
            Console.error("Server name is required to stop a server")
            return

        Console.ok(f"shutting down server {name}")
        registry = Registry()
        entries = registry.list(name=name)
        
        pid = None
        if len(entries) > 1:
            Console.error(f"Aborting, returned more than one entry from the Registry with the name {name}")
            return
        elif len(entries) == 1:
            pid = str(entries[0]['pid'])
        else:
            result = Server.ps(name=name)
            if result:
                pid = str(result[0]["pid"])

        if pid:
            try:
                Console.info(f"Killing process {pid}")
                Shell.kill_pid(pid)
                registry.delete(name=name)
            except Exception as e:
                Console.error(f"Failed to kill process {pid}: {e}")
        else:
            Console.error(f"No Cloudmesh OpenAPI Server found with the name {name}")


    def run_os(self) -> int:
        """
        Start an openapi server by creating a physical flask script

        :return:  pid for started server
        """
        Console.ok("starting server")

        today_dt = date.today().strftime("%m%d%Y")
        VERBOSE(f"spec path: {self.spec}")

        flask_script = textwrap.dedent(f'''
                import connexion
                import uvicorn

                # Create the application instance with FastAPI backend
                app = connexion.App(__name__, 
                                    specification_dir='{self.directory}',
                                    backend='fastapi')

                # Read the yaml file to configure the endpoints
                app.add_api('{self.spec}')

                # Add health check endpoint
                @app.app.get("/health")
                async def health_check():
                    return {{"status": "healthy", "server": "{self.name}"}}

                if __name__ == '__main__':
                    uvicorn.run(app, host='{self.host}', 
                                port={self.port}, 
                                log_level='info' if {self.debug} else 'warning')
            ''')

        script_path = Path(self.directory) / f"{self.name}_cmsoaserver.py"
        VERBOSE(f"server script: {script_path}")

        try:
            with open(script_path, 'w') as f:
                f.write(flask_script)
        except IOError as e:
            Console.error(f"Unable to write server file: {e}")
            raise

        pid = 0
        try:
            logname = Path(self.directory) / f"{self.name}_server.{today_dt}.log"
            with open(logname, "w") as log_file:
                process = subprocess.Popen([sys.executable, str(script_path)],
                                           stdout=log_file,
                                           stderr=subprocess.STDOUT,
                                           shell=False)
                pid = process.pid
            
            # Write PID file for robust process tracking
            pid_file = self._get_pid_file(self.name)
            with open(pid_file, "w") as f:
                f.write(str(pid))
                
        except Exception as e:
            Console.error(f"Unable to start server: {e}")
            raise

        try:
            with open(self.spec, "r") as stream:
                details = yaml.safe_load(stream)
        except (yaml.YAMLError, IOError) as e:
            Console.error(f"Yaml file has syntax error or is missing: {e}")
            raise

        url = details["servers"][0]["url"]

        print(f"\n   Starting: {self.name}")
        print(f"   PID:       {pid}")
        print(f"   Spec:      {self.spec}")
        print(f"   URL:       {url}\n")

        registry = Registry()
        ai_metadata = self._get_ai_metadata()
        
        registry.add_form_file(details,
                                pid=pid,
                                spec=self.spec,
                                directory=self.directory,
                                port=self.port,
                                host=self.host,
                                url=url,
                                **ai_metadata
                                )

        return pid
