from config.base import Paramiko
from config import host_config
import config
import paramiko
import os

def nginx_deploy(hosts):
    for host in hosts:
        p = Paramiko()

        # Base_dir = os.path.dirname(os.path.abspath(os.getcwd()))
        # print os.getcwd()
        # print os.path.join(Base_dir, 'config', 'id_rsa')
        key = paramiko.RSAKey.from_private_key_file(os.path.join(config.base.Base_dir,'config','id_rsa'))

        p.connect(host=host[0],user=host[1],key=key)
        p.upload(os.path.join(config.b ase.Base_dir,'nginx_deploy','nginx.zip'),'/opt/nginx.zip')
        p.cmd('unzip -o -d /opt /opt/nginx.zip')
        p.cmd('python /opt/nginx_deploy.py')
        p.cmd(r"sed -i '116 s%^%    include /usr/local/nginx1.10.2/conf/vhosts.d/*.conf;\n%' /usr/local/nginx1.10.2/conf/nginx.conf")
        p.cmd('mkdir /usr/local/nginx1.10.2/conf/vhosts.d')
        p.cmd('nginx -s reload')

if __name__ == '__main__':
    nginx_deploy(host_config.webserver)