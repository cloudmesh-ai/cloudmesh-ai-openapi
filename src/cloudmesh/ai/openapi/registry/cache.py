from cloudmesh.ai.openapi.registry.DataBaseDecorator import DatabaseUpdate
from cloudmesh.ai.openapi.registry.Registry import Registry
from pathlib import Path
from cloudmesh.ai.common.util import path_expand
from cloudmesh.ai.common.debug import VERBOSE
from cloudmesh.ai.common.io import Console
import pickle
from cloudmesh.ai.common.stopwatch import StopWatch
import os


class ResultCache:
    """Saves serialized model to local cache and saves metadata about the model to local db."""

    def __init__(self):
        """Initializes the ResultCache."""
        pass

    @DatabaseUpdate()
    def save(self, modelname=None, type="pickle", modelobject=None, **kwargs):
        """Save model to cache.

        Args:
            modelname (str, optional): The name of the model. Will be used to name registry entry.
            type (str): The type of serialization. Defaults to "pickle".
            modelobject (Any): The model object to be serialized.
            **kwargs: Any other parameters for the registry.

        Returns:
            Dict[str, Any]: The registry entry created for the cached model.
        """

        # create local cache directory
        cache_path = f"~/.cloudmesh/server-cache/{modelname}/"
        p = Path(path_expand(cache_path))
        p.mkdir(parents=True, exist_ok=True)

        # serialize model and save to local cache directory
        cached_file = ""
        if type == "pickle":
            cached_file = self._make_pickle(modelname, modelobject, str(p.absolute()))
        else:
            Console.error(f"Unsupported serialization type provided : {type}")
            raise Exception

        # update db cache with below details
        entry = {
            "cm": {
                "cloud": "local",
                "kind": "cache",
                "name": modelname,
                "driver": None
            },
            "name": modelname,
            "status": "cached",
            "cached_file": cached_file
        }

        for key in kwargs:
            entry[key] = kwargs[key]

        return entry

    def load(self, name):
        """Load cached model.

        Args:
            name (str): Model name or cached file name.

        Returns:
            Any: The unserialized model object.

        Raises:
            FileNotFoundError: If no cache entry is found for the given name.
        """

        # USER env variable is required by StopWatch
        if os.getenv('USER'):
            # Do nothing
            VERBOSE("USER env variable is already defined")
        else:
            os.environ['USER'] = 'No USER env var defined'

        registry = Registry()
        entries = registry.list(name=name)
        if not entries:
            raise FileNotFoundError(f"No cache entry found for {name}")
        
        cached_file = entries[0]['cached_file']
        Console.info(f"Loading serialized model: {cached_file}")
        StopWatch.start(f"Load pickle {name}")
        deserialized_model = self._load_pickle(cached_file)
        StopWatch.stop(f"Load pickle {name}")
        time_taken = StopWatch.get(f"Load pickle {name}")

        # TODO: figure out how useful the duration is and return to client if required
        deserialized_model_dict = {
            "model_name": name,
            "model_object": deserialized_model,
            "duration": time_taken  # duration of deserialization function
        }
        return deserialized_model

    def _make_pickle(self, title, data, path):
        """Serializes a model and returns the fully qualified path and file name to pickle file.

        Args:
            title (str): Pickle file name.
            data (Any): Model object to serialize.
            path (str): Path to the pickle file.

        Returns:
            str: The fully qualified path to the pickle file.
        """

        file = Path(f"{path}/{title}.pickle")
        pikd = open(file, "wb")
        pickle.dump(data, pikd)
        pikd.close()

        return str(file)

    def _load_pickle(self, file):
        """Loads a pickle file and returns the object.

        Args:
            file (str): Path to the pickle file.

        Returns:
            Any: The unpickled model object.
        """

        pikd = open(file, "rb")
        data = pickle.load(pikd)
        pikd.close()
        return data


if __name__ == "__main__":

    from sklearn.linear_model import LogisticRegression
    from sklearn.datasets import load_iris


    newcache = ResultCache()

    X, y = load_iris(return_X_y=True)
    # print(X)
    clf = LogisticRegression(random_state=0, max_iter=300).fit(X, y)
    print(newcache.save("irismodel1", "pickle", clf))
    print("finished caching model")
    #model_dict = newcache.load("irismodel1")
    model = newcache.load("irismodel1")
    #print(model_dict['model_object'].predict(X[:2, :]))
    print(model.predict(X[:2, :]))
