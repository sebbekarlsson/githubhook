from flask import Flask, request, jsonify

import logging
import os

from functools import wraps

from githubhook.deploy import download_file, deploy_app
from githubhook import config


app = Flask(__name__)

app.config.update(
    SECRET_KEY='abc123',
    TEMPLATES_AUTO_RELOAD=True
)


def validate_response(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        data = request.get_json()

        if not data:
            return jsonify({'message': 'No data was received'}), 400

        if 'zen' in data:
            return jsonify({'message': 'Hello'}), 200

        if 'commits' not in data:
            return jsonify({
                'message':
                'This event does not appear to be a `push` event.'
            }), 400

        return f(*args, **kwargs)
    return wrapper


@app.route('/', methods=['POST', 'GET'])
@validate_response
def hook():
    data = request.get_json()

    repo_name = data['repository']['name']

    if repo_name in config['repositories'].keys():
        clone_url = data['repository']['ssh_url']

        logging.info('Downloading {}...'.format(str(clone_url)))

        download_file(
            clone_url,
            os.path.join(
                config['directory'],
                repo_name
            )
        )

        project_config = config['repositories'][repo_name]

        logging.info('Deploying application...')

        deploy_app(app_name=repo_name, **project_config['nginx'])

    return jsonify({'message': 'Thank you'})
