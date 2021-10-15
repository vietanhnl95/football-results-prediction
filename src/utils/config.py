import yaml


def read_config():
    """Read yaml file and return the config as a dictionary"""
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config
