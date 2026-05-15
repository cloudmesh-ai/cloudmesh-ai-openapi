from cloudmesh.ai.common.Shell import Shell
from cloudmesh.ai.openapi.registry.DataBaseDecorator import DatabaseUpdate
from cloudmesh.ai.openapi.registry.PickleDB import PickleDB


class RegistryPickle:
    """Helps to register services into the database, which is later used to stop servers."""
    kind = "register"

    collection = "local-registry"

    output = {
        "register": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "status",
                      "url",
                      "pid"],
            "header": ["Name",
                       "Status",
                       "Url",
                       "Pid"]
        }
    }

    def load(self, filename="~/.cloudmesh/openapi/registry.p"):
        """Loads the registry content.

        Args:
            filename (str): Path to the registry pickle file. Defaults to "~/.cloudmesh/openapi/registry.p".
        """
        self.data = PickleDB(filename=filename)

    def clean(self, filename="~/.cloudmesh/openapi/registry.p"):
        """Erases the registry content from the file while keeping the file.

        The resulting data in the file will be empty.

        Args:
            filename (str): Path to the registry pickle file. Defaults to "~/.cloudmesh/openapi/registry.p".

        Returns:
            Any: The result of the clean operation.
        """
        return PickleDB(filename=filename).clean()

    # noinspection PyPep8Naming

    def Print(self, data, output=None):
        """Print output in a structured format.

        Args:
            data (Any): Input data to be printed out.
            output (Optional[str]): Type of structured output.

        Returns:
            Any: The structured output.
        """

        if output == "table":

            order = self.output[RegistryPickle.kind]['order']  # not pretty
            header = self.output[RegistryPickle.kind]['header']  # not pretty
            # humanize = self.output[kind]['humanize']  # not pretty

            print(data)
        else:
            print(data)

    @DatabaseUpdate(provider="pickle")
    def add(self, name=None, **kwargs):
        """Add an entry to the registry.

        Args:
            name (Optional[str]): Name to be used for the registry entry.
            **kwargs: Other optional fields to populate in the registry.

        Returns:
            Dict[str, Any]: The registry entry created.
        """
        entry = {
            "cm": {
                "cloud": "local",
                "kind": "registry",
                "name": name,
                "driver": None
            },
            "name": name,
            "status": "defined"
        }

        for key in kwargs:
            entry[key] = kwargs[key]

        return entry

    def add_form_file(self, filename, **kwargs):
        """Add an entry to the registry from a file.

        Args:
            filename (str): File name including path.
            **kwargs: Other optional fields to populate in the registry.

        Returns:
            Dict[str, Any]: The entry to be inserted into the Registry.
        """

        spec = filename

        title = spec["info"]["title"]

        registry = RegistryPickle()
        entry = registry.add(name=title, **kwargs)

        return entry

    def delete(self, name=None):
        """Delete an item from the registry.

        Args:
            name (Optional[str]): Name of the item in the registry.

        Returns:
            Any: The result of the delete operation.
        """
        cm = PickleDB()  # repalce by pickle
        entries = cm.delete(name)
        return entries

    def list(self, name=None):
        """List entries in the registry.

        Args:
            name (Optional[str]): Name of the registered server. 
                If not passed, will list all registered servers.

        Returns:
            List[Any]: A list of registered server(s).
        """
        cm = PickleDB()

        if name == None:
            entries = cm.find(cloud="local", kind="registry")
        else:
            entries = cm.find_name(name=name, kind="registry")

        return entries

    # TODO: determine if these are still needed as these functions are handled by cms already
    '''
    def start(self):
        """
        start the registry

        possibly not needed as we have cms start

        :return:
        """
        r = Shell.cms("start")

    def stop(self):
        """
        stop the registry

        possibly not needed as we have cms start

        :return:
        """
        r = Shell.cms("stop")
    '''
