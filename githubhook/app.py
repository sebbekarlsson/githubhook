from githubhook import config

from flask import Flask, request, jsonify
import git

import os
import shutil

from jinja2 import Template

import subprocess


app = Flask(__name__)

app.config.update(
    SECRET_KEY='abc123',
    TEMPLATES_AUTO_RELOAD=True
)


def download_file(url, path):
    if os.path.isdir(path):
        os.rmdir(path)

    git_ssh_identity_file = os.path.expanduser('~/.ssh/id_rsa')
    git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file

    with git.Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        git.Repo.clone_from(url, path, branch='master')


def deploy_app(app_name, server_names, https, python):
    app_path = '/var/www/{}'.format(app_name)

    if not os.path.isdir(app_path):
        os.makedirs(app_path)

    nginx_template = Template(open('nginx/nginx.nginx').read())
    ini_template = Template(open('nginx/ini.ini').read())
    systemd_template = Template(open('nginx/systemd.service').read())

    full_dir = os.path.join(app_path, app_name)

    if os.path.isdir(full_dir):
        shutil.rmtree(full_dir)

    shutil.move(os.path.join(config['directory'], app_name), app_path)

    open(os.path.join('/etc/nginx/sites-enabled', '{}.nginx'.format(app_name)), 'w+').write(  # NOQA E501
        nginx_template.render(
            server_names=server_names,
            https=https,
            app_name=app_name,
            python=python
        )
    )

    open(os.path.join(app_path, '{}.ini'.format(app_name)), 'w+').write(
        ini_template.render(
            server_names=server_names,
            https=https,
            app_name=app_name,
            python=python
        )
    )

    open(os.path.join('/etc/systemd/system/', '{}.service'.format(app_name)), 'w+').write(  # NOQA E501
        systemd_template.render(
            server_names=server_names,
            https=https,
            app_name=app_name,
            python=python
        )
    )

    subprocess.Popen('systemctl daemon reload', shell=True, stdout=subprocess.PIPE).stdout.read()
    subprocess.Popen('systemctl restart {}.service'.format(app_name), shell=True, stdout=subprocess.PIPE).stdout.read()
    subprocess.Popen('systemctl restart nginx', shell=True, stdout=subprocess.PIPE).stdout.read()


@app.route('/', methods=['POST', 'GET'])
def hook():
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data was received'}), 400

    if 'commits' in data:
        repo_name = data['repository']['name']

        if repo_name in config['repositories'].keys():
            clone_url = data['repository']['ssh_url']

            download_file(
                clone_url,
                os.path.join(
                    config['directory'],
                    repo_name
                )
            )

            project_config = config['repositories'][repo_name]
            deploy_app(app_name=repo_name, **project_config['nginx'])

    return jsonify({'message': 'Thank you'})
