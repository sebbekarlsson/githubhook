import json
import os
import logging


config = json.loads(open('config.json').read())

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG,
    filename=config.get('log', 'githubhook.log')
)

if not os.path.isdir(config['directory']):
    os.makedirs(config['directory'])
