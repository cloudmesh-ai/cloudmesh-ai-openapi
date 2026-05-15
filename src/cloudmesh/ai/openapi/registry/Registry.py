from cloudmesh.ai.common.config import Config
from cloudmesh.ai.common.io import Console
from cloudmesh.ai.openapi.registry.RegistryPickle import RegistryPickle


class Registry:
    """
      This class serves as a wrapper for either Registrypickle or RegistryMongoDatabase
    """

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
        """
        Initialize the Registry using the pickle protocol.
        """
        Registry.PROTOCOL_NAME = "pickle"
        self.protocol = RegistryPickle()
        Console.ok(f"INIT: Using {Registry.PROTOCOL_NAME} Protocol")

    @classmethod
    def protocol(cls, protocol="pickle"):
        """
        Force the protocol to pickle.
        """
        cls.PROTOCOL_NAME = "pickle"
        Config().set(cls.RESGISTRY_CONFIG, "pickle")
        return cls.PROTOCOL_NAME

    # noinspection PyPep8Naming
    def Print(self, data, output=None):
        """
        print output in a structured format

        :param data:  input data to be printed out
        :param output:  type of structured output
        :return:  structured output
        """
        Console.ok(f"PRINT: Using {Registry.PROTOCOL_NAME} Protocol")
        self.protocol.Print(data, output)

    def add(self, name=None, **kwargs):
        """
        add to registry

        :param name: name to be used for registry entry
        :param kwargs:  other optional fields to populate in registry
        :return:  
        """
        Console.ok(f"ADD: Using {Registry.PROTOCOL_NAME} Protocol")
        return self.protocol.add(name, **kwargs)

    def add_form_file(self, filename, **kwargs):
        """
        add to registry from file

        :param filename: file name including path
        :return:  entry to be inserted into Registry
        """
        Console.ok(f"ADD FROM FILE: Using {Registry.PROTOCOL_NAME} Protocol")
        return self.protocol.add_form_file(filename, **kwargs)

    def delete(self, name=None):
        """
        delete item from registry

        :param name: name of the item in registry
        :return:  
        """
        Console.ok(f"DELETE: Using {Registry.PROTOCOL_NAME} Protocol")
        return self.protocol.delete(name)

    def list(self, name=None):
        """
        list entries in the registry

        :param name:  name of registered server.  If not passed will list all registered servers.
        :return:  list of registered server(s)
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
