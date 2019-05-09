import json
import os


config = json.loads(open('config.json').read())


if not os.path.isdir(config['directory']):
    os.makedirs(config['directory'])
