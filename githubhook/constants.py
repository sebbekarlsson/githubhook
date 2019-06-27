from jinja2 import Template


SERVER_APPLICATION_PATH = '/var/www'
SERVER_SYSTEMD_PATH = '/etc/systemd/system'
SERVER_SOCKET_PATH = '/var/run'
SERVER_NGINX_PATH = '/etc/nginx/sites-enabled'
SERVER_LOG_PATH = '/var/log'

TEMPLATE_NGINX = Template(open('nginx/nginx.nginx').read())
TEMPLATE_SYSTEMD = Template(open('nginx/systemd.service').read())
TEMPLATE_UWSGI_INI = Template(open('nginx/ini.ini').read())
