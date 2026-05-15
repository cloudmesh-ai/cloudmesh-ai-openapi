from cloudmesh.ai.common.config import Config
from cloudmesh.ai.common.io import Console
from cloudmesh.ai.openapi.registry.RegistryPickle import RegistryPickle


class Registry:
    """Wrapper for either RegistryPickle or RegistryMongoDatabase."""

    kind = "registry"

    sample = """
    cloudmesh:
      cloud:
        {name}:
          cm:
            active: true
            heading: microservice registry
            host: TBD
            label: {name}
            kind: registry
            version: TBD
            service: registry
          default:
            kind: pickle
    """

    PROTOCOL_NAME = None
    RESGISTRY_CONFIG = "cloudmesh.ai.registry.microservice.default.protocol"

    def __init__(self):
        """Initializes the Registry using the pickle protocol."""
        Registry.PROTOCOL_NAME = "pickle"
        self.protocol = RegistryPickle()
        Console.ok(f"INIT: Using {Registry.PROTOCOL_NAME} Protocol")

    @classmethod
    def protocol(cls, protocol="pickle"):
        """Force the protocol to pickle.

        Args:
            protocol (str): The protocol to use. Defaults to "pickle".

        Returns:
            str: The protocol name.
        """
        cls.PROTOCOL_NAME = "pickle"
        Config().set(cls.RESGISTRY_CONFIG, "pickle")
        return cls.PROTOCOL_NAME

    # noinspection PyPep8Naming
    def Print(self, data, output=None):
        """Print output in a structured format.

        Args:
            data (Any): Input data to be printed out.
            output (Optional[str]): Type of structured output.

        Returns:
            Any: The structured output.
        """
        Console.ok(f"PRINT: Using {Registry.PROTOCOL_NAME} Protocol")
        self.protocol.Print(data, output)

    def add(self, name=None, **kwargs):
        """Add an entry to the registry.

        Args:
            name (Optional[str]): Name to be used for the registry entry.
            **kwargs: Other optional fields to populate in the registry.

        Returns:
            Any: The result of the add operation.
        """
        Console.ok(f"ADD: Using {Registry.PROTOCOL_NAME} Protocol")
        return self.protocol.add(name, **kwargs)

    def add_form_file(self, filename, **kwargs):
        """Add an entry to the registry from a file.

        Args:
            filename (str): File name including path.
            **kwargs: Other optional fields to populate in the registry.

        Returns:
            Any: The entry to be inserted into the Registry.
        """
        Console.ok(f"ADD FROM FILE: Using {Registry.PROTOCOL_NAME} Protocol")
        return self.protocol.add_form_file(filename, **kwargs)

    def delete(self, name=None):
        """Delete an item from the registry.

        Args:
            name (Optional[str]): Name of the item in the registry.

        Returns:
            Any: The result of the delete operation.
        """
        Console.ok(f"DELETE: Using {Registry.PROTOCOL_NAME} Protocol")
        return self.protocol.delete(name)

    def list(self, name=None):
        """List entries in the registry.

        Args:
            name (Optional[str]): Name of the registered server. 
                If not passed, will list all registered servers.

        Returns:
            List[Any]: A list of registered server(s).
        """
        Console.ok(f"LIST: Using {Registry.PROTOCOL_NAME} Protocol")
        return self.protocol.list(name)

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
