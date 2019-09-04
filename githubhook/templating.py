import os

from githubhook.constants import (
    SERVER_APPLICATION_PATH,
    SERVER_SYSTEMD_PATH,
    SERVER_NGINX_PATH,
    TEMPLATE_NGINX,
    TEMPLATE_SYSTEMD,
    TEMPLATE_UWSGI_INI
)


def write_nginx_template(
    server_names,
    https,
    app_name,
    python,
    public=''
):
    open(os.path.join(SERVER_NGINX_PATH, app_name + '.nginx'), 'w+').write(
        TEMPLATE_NGINX.render(
            server_names=server_names,
            https=https,
            app_name=app_name,
            python=python,
            public=public
        )
    )


def write_systemd_template(app_name):
    open(os.path.join(SERVER_SYSTEMD_PATH, app_name + '.service'), 'w+').write(
        TEMPLATE_SYSTEMD.render(
            app_name=app_name
        )
    )


def write_ini_template(app_name):
    open(os.path.join(
        SERVER_APPLICATION_PATH,
        '{}/{}/{}.ini'.format(app_name, app_name, app_name)), 'w+'
    )\
        .write(TEMPLATE_UWSGI_INI.render(app_name=app_name))
