from cloudmesh.ai.openapi.registry.PickleDB import PickleDB


class DatabaseUpdate:
    """Decorator that automatically replaces an entry in the database with the dictionary returned by a function.

    It is added to the registry. The location is determined from the values in the dictionary.
    The name of the collection is determined from cloud and kind: `cloud-kind`.
    In addition, each entry in the collection has a name that must be unique in that collection.

    In most examples, it is best to separate the upload from the actual return class. 
    This way we essentially provide two functions: one that provides the dict and 
    another that is responsible for the upload to the database.

    Example:
        cloudmesh.example.foo contains:
            class Provider(object)
                def entries(self):
                    return {
                       "cm": {
                          "cloud": "foo",
                          "kind": "entries",
                          "name": "test01",
                          "test": "hello"}
                    }

        cloudmesh.example.bar contains:
            class Provider(object)
                def entries(self):
                    return {
                       "cloud": "bar",
                       "kind": "entries",
                       "name": "test01",
                       "test": "hello"}

        cloudmesh.example.provider.foo:
            from cloudmesh.example.foo import Provider as FooProvider
            from cloudmesh.example.foo import Provider as BarProvider

            class Provider(object)
                def __init__(self, provider):
                   if provider == "foo":
                       provider = FooProvider()
                    elif provider == "bar":
                       provider = BarProvider()

                @DatabaseUpdate
                def entries(self):
                    provider.entries()

    Separating the database and the dictionary creation allows the developer to
    implement different providers but only use one class with the same methods
    to interact for all providers with the database.

    In the combined provider, a find function to for example search for entries
    by name across collections could be implemented.
    """

    # noinspection PyUnusedLocal
    def __init__(self, provider="pickle", **kwargs):
        """Initializes the DatabaseUpdate decorator.

        Args:
            provider (str): The database provider to use. Defaults to "pickle".
            **kwargs: Additional configuration for the database.
        """
        self.database = PickleDB()

    def __call__(self, f):
        """Wraps the function to automatically update the database with its return value.

        Args:
            f (callable): The function to be decorated.

        Returns:
            callable: The wrapper function that handles the database update.
        """
        def wrapper(*args, **kwargs):
            current = f(*args, **kwargs)
            if type(current) == dict:
                current = [current]

            if current is None:
                return []

            result = self.database.update(current)
            return result

        return wrapper




class DatabaseAlter:
    """Decorator that automatically alters an entry in the database with the dictionary returned by a function.

    It is added to the registry. The location is determined from the values in the dictionary.
    The name of the collection is determined from cloud and kind: `cloud-kind`.
    In addition, each entry in the collection has a name that must be unique in that collection.

    In most examples, it is best to separate the upload from the actual return class. 
    This way we essentially provide two functions: one that provides the dict and 
    another that is responsible for the upload to the database.

    Example:
        cloudmesh.example.foo contains:
            class Provider(object)
                def entries(self):
                    return {
                       "cm": {
                          "cloud": "foo",
                          "kind": "entries",
                          "name": "test01",
                          "test": "hello"}
                    }

        cloudmesh.example.bar contains:
            class Provider(object)
                def entries(self):
                    return {
                       "cloud": "bar",
                       "kind": "entries",
                       "name": "test01",
                       "test": "hello"}

        cloudmesh.example.provider.foo:
            from cloudmesh.example.foo import Provider as FooProvider
            from cloudmesh.example.foo import Provider as BarProvider

            class Provider(object)
                def __init__(self, provider):
                   if provider == "foo":
                       provider = FooProvider()
                    elif provider == "bar":
                       provider = BarProvider()

                @DatabaseUpdate
                def entries(self):
                    provider.entries()

    Separating the database and the dictionary creation allows the developer to
    implement different providers but only use one class with the same methods
    to interact for all providers with the database.

    In the combined provider, a find function to for example search for entries
    by name across collections could be implemented.
    """

    # noinspection PyUnusedLocal
    def __init__(self, **kwargs):
        """Initializes the DatabaseAlter decorator.

        Args:
            **kwargs: Additional configuration for the database.
        """
        self.database = PickleDB()

    def __call__(self, f):
        """Wraps the function to automatically alter the database with its return value.

        Args:
            f (callable): The function to be decorated.

        Returns:
            callable: The wrapper function that handles the database alteration.
        """
        def wrapper(*args, **kwargs):
            current = f(*args, **kwargs)
            if type(current) == dict:
                current = [current]

            result = self.database.alter(current)
            return result

        return wrapper
