import yaml
from pathlib import Path


class Config:
    config = {}
    filepath = ''

    def __init__(self, filepath=''):
        self.filepath = filepath
        self.load(self.filepath)

    def put(self, key, value):
        self.config[key] = value

    def get(self, key, default=None):
        if key in self.config.keys():
            return self.config[key]
        elif default is None:
            raise NotImplementedError(f"Can't get {key} from config, it doesn't exist!")
        else:
            return default

    def load(self, filepath):
        if filepath:
            with open(Path(filepath).resolve()) as file:
                # The FullLoader parameter handles the conversion from YAML
                # scalar values to Python the dictionary format
                self.config = yaml.load(file, Loader=yaml.FullLoader)
                if not self.config:
                    self.config = {}

    def save(self, filepath=''):
        if not filepath:
            filepath = self.filepath
            assert filepath
        with open(filepath, 'w') as file:
            yaml.dump(self.config, file)

