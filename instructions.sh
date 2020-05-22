rm -rf /var/www/githubhook/githubhook
mkdir -p /var/www/githubhook
mv githubhook /var/www/githubhook/.
cd /var/www/githubhook/githubhook

cp githubhook.nginx /etc/nginx/sites-available/githubhook.nginx
ln -s /etc/nginx/sites-available/githubhook.nginx /etc/nginx/sites-enabled/.

cp githubhook.service /etc/systemd/system/.

rm -rf ./venv
virtualenv -p /usr/bin/python3.7m ./venv
source ./venv/bin/activate
python setup.py develop

chown -R www-data:www-data /var/www/githubhook

touch /var/run/githubhook.sock
chmod -R 777 /var/run/githubhook.sock

systemctl daemon-reload
systemctl restart nginx
systemctl restart githubhook.service

touch /var/run/githubhook.sock
chmod -R 777 /var/run/githubhook.sock
