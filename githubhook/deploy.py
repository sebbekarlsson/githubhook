import os
import git
import shutil
import logging
import subprocess

from githubhook import config
from githubhook.constants import (
    SERVER_APPLICATION_PATH,
    SERVER_SOCKET_PATH,
    SERVER_LOG_PATH
)
from githubhook.templating import (
    write_ini_template,
    write_nginx_template,
    write_systemd_template
)


def touch(fname):
    try:
        try:
            os.utime(fname, None)
        except OSError:
            open(fname, 'a').close()

        open(fname, 'w+').write('\n')
    except Exception:
        logging.warning('Could not touch {}'.format(fname))


def download_file(url, path):
    if os.path.isdir(path):
        os.rmdir(path)

    git_ssh_identity_file = os.path.expanduser('~/.ssh/id_rsa')
    git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file

    with git.Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        git.Repo.clone_from(url, path, branch='master')



def get_usable_python_bin():
    bins = [
        '/usr/bin/python3.7m',
        '/usr/bin/python3.7',
        '/usr/bin/python3.6m',
        '/usr/bin/python3.6',
        '/usr/bin/python2.7'
    ]

    binfiles = list(filter(lambda x: os.path.isfile(x), bins))

    return binfiles[0] if binfiles else None


def deploy_app_python(app_name, full_dir):
    socket_path = os.path.join(SERVER_SOCKET_PATH, '{}.sock'.format(app_name))
    log_path = os.path.join(SERVER_LOG_PATH, '{}.log'.format(app_name))

    logging.info('Touching...')

    touch(socket_path)
    touch(log_path)

    logging.info('Chmoding...')

    os.chmod(socket_path, 0o777)
    os.chmod(log_path, 0o777)

    logging.info('Generating python uwsgi config...')

    write_ini_template(app_name=app_name)

    logging.info('Generating systemd service file...')

    write_systemd_template(app_name=app_name)

    logging.info('Creating virtualenv and running setup...')

    python_bin = get_usable_python_bin()

    if not python_bin:
        raise Exception('No python bin found')

    logging.info(f'Using python bin: {python_bin}')

    subprocess.Popen(f'''
        cd {full_dir};
        virtualenv -p {python_bin} ./venv;
        ./venv/bin/python setup.py install;
        ./venv/bin/python setup.py develop;
    '''.format(
        full_dir=full_dir,
        app_name=app_name
    ), shell=True, stdout=subprocess.PIPE).stdout.read()

    logging.info('Reloading and restarting systemd daemon...')

    subprocess.Popen('systemctl daemon-reload', shell=True, stdout=subprocess.PIPE).stdout.read()  # NOQA E501
    subprocess.Popen('systemctl restart {}.service'.format(app_name), shell=True, stdout=subprocess.PIPE).stdout.read()  # NOQA E501

    return socket_path


def deploy_app(app_name, server_names, https, python, public='', build_cmd=None):
    app_path = os.path.join(SERVER_APPLICATION_PATH, app_name)

    if not os.path.isdir(app_path):
        os.makedirs(app_path)

    full_dir = os.path.join(app_path, app_name)

    if os.path.isdir(full_dir):
        shutil.rmtree(full_dir)

    shutil.move(os.path.join(config['directory'], app_name), app_path)

    logging.info('Running build_cmd: {} in {}'.format(build_cmd, full_dir))

    subprocess.Popen('''
        cd {full_dir};
        {build_cmd}
    '''.format(
        full_dir=full_dir,
        build_cmd=build_cmd
    ), shell=True, stdout=subprocess.PIPE).stdout.read()

    logging.info('Generating nginx config...')

    write_nginx_template(
        server_names=server_names,
        https=https,
        app_name=app_name,
        python=python,
        public=public
    )

    socket_path = None

    if python:
        socket_path = deploy_app_python(app_name, full_dir)

    logging.info('Restarting nginx...')

    subprocess.Popen('systemctl restart nginx', shell=True, stdout=subprocess.PIPE).stdout.read()  # NOQA E501

    if python and socket_path:
        logging.info('chmod {}...'.format(socket_path))

        subprocess.Popen('''
            touch {socket_path};
            chmod -R 777 {socket_path};
        '''.format(
            socket_path=socket_path
        ), shell=True, stdout=subprocess.PIPE).stdout.read()
