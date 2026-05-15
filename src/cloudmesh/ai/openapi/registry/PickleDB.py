import os
import pickle
from cloudmesh.ai.common.util import path_expand
from cloudmesh.ai.common.io import Console


class PickleDB:
    """A simple database implementation using Python's pickle module for persistence."""

    def __init__(self, filename="~/.cloudmesh/openapi/registry.p"):
        """Initializes the PickleDB and loads existing data from the file.

        Args:
            filename (str): Path to the pickle file. Defaults to "~/.cloudmesh/openapi/registry.p".
        """
        expanded_filename = path_expand(filename)
        os.makedirs(os.path.dirname(expanded_filename), exist_ok=True)
        self.DB_PATH = expanded_filename

        # Attempt to load from pkl
        try:
            self.db = pickle.load(open(expanded_filename, "rb"))
        except FileNotFoundError as e:
            self.db = {}

    def update(self, entries):
        """Updates the database with new entries.

        Args:
            entries (List[Dict]): A list of entries to add or update. Each entry must have a 'name' key.

        Returns:
            List[Dict]: The list of entries that were successfully updated.

        Raises:
            KeyError: If an entry is missing the 'name' key.
        """
        result = []
        for entry in entries:
            if "name" not in entry:
                raise KeyError(
                    f"No name given for DB entry: {entry}")
            self.db[entry['name']] = entry
            result += [entry]
        return result

    def close_client(self):
        """Persists the current database state to the pickle file.

        Returns:
            int: 0 if successful, -1 if an error occurred.
        """
        try:
            pickle.dump(self.db, open(self.DB_PATH, "wb"))
            return 0
        except Exception as e:
            Console.error(f"Error writing to PickleDB: {e}")
            return -1

    def clean(self):
        """Clears all entries from the database and updates the pickle file.

        Returns:
            int: 0 if successful, -1 if an error occurred.
        """
        try:
            pickle.dump({}, open(self.DB_PATH, "wb"))
            self.db = {}
            return 0
        except:
            Console.error(f"Error clearing PickleDB at {self.DB_PATH}")
            return -1

    def delete(self, name):
        """Deletes an entry from the database by name.

        Args:
            name (str): The name of the entry to delete.

        Returns:
            Optional[Dict]: The deleted entry if found, otherwise None.
        """
        try:
            entry = self.db[name]
            del self.db[name]
            return [entry]
        except KeyError as e:
            Console.error(
                f"KeyError: Could not delete {name} from db. Skipping")

    def find(self, cloud, kind=None):
        """Finds entries in the database matching the cloud and kind.

        Args:
            cloud (str): The cloud name to filter by.
            kind (Optional[str]): The kind of entry to filter by.

        Returns:
            List[Dict]: A list of matching entries.
        """
        entries = []
        for entry in self.db:
            try:
                if self.db[entry]["cm"]["cloud"] == cloud and self.db[entry]["cm"]["kind"] == kind:
                    entries += [self.db[entry]]
            except KeyError as e:
                Console.error(f"KeyError in PickleDB.find() Skipping: {e}")
        return entries

    def find_name(self, name, kind=None):
        """Finds an entry in the database by its name and kind.

        Args:
            name (str): The name of the entry to find.
            kind (Optional[str]): The kind of entry to filter by.

        Returns:
            List[Dict]: A list containing the matching entry if found, otherwise an empty list.
        """
        entries = []
        try:
            if self.db[name]["cm"]["kind"] == kind:
                entries += [self.db[name]]
        except KeyError as e:
            Console.error(f"KeyError. Skipping: {e}")
        return entries
