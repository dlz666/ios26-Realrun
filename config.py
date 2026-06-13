import yaml

class Config:
    def __init__(self):
        with open("config.yaml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        for i in config:
            setattr(self, i, config[i])


config = Config()
