import hashlib
import hmac
import textwrap
import json
from pathlib import Path

from shutil import copyfile

from cloudmesh.ai.common.io import Console
from cloudmesh.ai.common.util import path_expand
from cloudmesh.ai.common.Shell import Shell
from cloudmesh.ai.common.config import Config

class BasicAuth:
    """Handles basic authentication for OpenAPI services.

    It supports multiple users with hashed passwords stored in a local file.
    Reference: https://swagger.io/docs/specification/2-0/authentication/basic-authentication/
    """
    CONFIG_ATTRIBUTE_AUTH = 'cloudmesh.ai.openapi.authentication'
    CONFIG_VALUE_AUTH = 'basic'
    HALT_FLAG = '#### basic_auth functionality added'
    USERS_FILE = Path(path_expand('~/.cloudmesh/.auth_users.json'))

    AUTH_FUNC_TEMPLATE = textwrap.dedent("""
    from cloudmesh.ai.openapi.authentication.basic import BasicAuth

    def basic_auth(username, password, required_scopes=None):
        return BasicAuth.basic_auth(username, password)
    
    {halt_flag}
    """)

    @classmethod
    def basic_auth(cls, username, password, required_scopes=None):
        """Basic authentication function to be listed as x-basicInfoFunc in generated OpenAPI YAML.

        Args:
            username (str): The username to authenticate.
            password (str): The password to verify.
            required_scopes (Optional[List[str]]): Optional list of required scopes.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing 'sub' and 'scope' if authenticated, 
                otherwise None.
        """
        try:
            if not cls.USERS_FILE.exists():
                return None
            
            with open(cls.USERS_FILE, "r") as f:
                users = json.load(f)
            
            if username in users:
                stored_hash = users[username]['hash']
                salt = users[username]['salt']
                if cls._hash_password(password, salt) == stored_hash:
                    return {'sub': username, 'scope': users[username].get('scope', '')}
        except Exception as e:
            Console.error(f"Auth error: {e}")
            
        return None

    @classmethod
    def reset_users(cls):
        """DEPRECATED."""
        pass

    @classmethod
    def add_user(cls, user, password, scope=""):
        """Add a user with a hashed password to the auth file.

        Args:
            user (str): The username to add.
            password (str): The plain-text password to hash and store.
            scope (str): The scope associated with the user. Defaults to "".
        """
        import os
        salt = os.urandom(16).hex()
        hashed = cls._hash_password(password, salt)
        
        users = {}
        if cls.USERS_FILE.exists():
            with open(cls.USERS_FILE, "r") as f:
                try:
                    users = json.load(f)
                except json.JSONDecodeError:
                    pass
        
        users[user] = {'hash': hashed, 'salt': salt, 'scope': scope}
        
        cls.USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(cls.USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)
        
        Console.ok(f"User {user} added successfully")

    @classmethod
    def _hash_password(cls, password, salt):
        """Hash password using SHA256 and a salt.

        Args:
            password (str): The plain-text password.
            salt (str): The salt to use for hashing.

        Returns:
            str: The resulting hex digest of the hashed password.
        """
        return hmac.new(salt.encode(), password.encode(), hashlib.sha256).hexdigest()

    @classmethod
    def write_basic_auth(cls, filename, module_name):
        """Writes the basic auth configuration to a new python file.

        Args:
            filename (str): The original python file name.
            module_name (str): The original module name.

        Returns:
            Tuple[str, str]: A tuple containing the new module name and the new filename.
        """
        basic_auth_enabled = False
        for line in open(filename):
            if cls.HALT_FLAG in line:
                basic_auth_enabled = True
                break

        if not basic_auth_enabled:
            filename_auth = filename[:-len('.py')] + '_basic_auth_enabled.py'
            copyfile(filename, filename_auth)
            Console.info(f'copied {filename} to {filename_auth}')
            filename = filename_auth
            module_name = module_name + '_basic_auth_enabled'
            with open(filename, 'a') as f:
                f.write('\n')
                f.write(cls.AUTH_FUNC_TEMPLATE.format(halt_flag=cls.HALT_FLAG))
                f.close()
            Console.info(f'added basic auth functionality to {filename}')

        return module_name, filename
