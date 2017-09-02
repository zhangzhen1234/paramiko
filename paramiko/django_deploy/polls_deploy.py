#coding:utf8
from config.base import Paramiko
from config import host_config
import config
import paramiko
import os

def django_deploy():
    for host in host_config.webserver:
        p = Paramiko()
        key = paramiko.RSAKey.from_private_key_file(os.path.join(config.base.Base_dir, 'config', 'id_rsa'))
        p.connect(host=host[0],user=host[1],key=key)
        # 创建虚拟环境
        p.cmd('virtualenv /root/pythonenv/django1.8')

        #上传项目解压
        # p.upload('polls.zip','/projects/polls.zip')
        p.upload(os.path.join(config.base.Base_dir,'django_deploy','polls.zip'),'/projects/polls.zip')
        p.cmd('unzip -d /projects -o /projects/polls.zip')

        #安装项目依赖
        p.cmd('yum -y install mysql-devel')
        p.cmd('/root/pythonenv/django1.8/bin/pip install -r /projects/polls/requirements')

        # supervisor安装启动
        suervisor_install(p)
        nginx_server(p)

def suervisor_install(p):
    p.cmd(r'rpm -Uvh https://mirrors.tuna.tsinghua.edu.cn/epel//7/x86_64/e/epel-release-7-10.noarch.rpm')
    p.cmd('rm -rf /var/run/yum.pid')
    p.cmd('yum -y install supervisor')
    p.upload(os.path.join(config.base.Base_dir,'django_deploy','polls.ini'),'/etc/supervisord.d/polls.ini')
    p.cmd('systemctl start supervisord.service')
    p.cmd('supervisorctl reload') #如果启动重新加载配置文件

def nginx_server(p):
    with open(os.path.join(config.base.Base_dir,'config','servertpl.conf'),'r') as f:
        content = f.read().replace('{{server_name}}',p.host)  #返回读取servertpl.conf里面的内容，紧该变了server_name的变量
        with open('polls.conf','w') as poll_f:
            poll_f.write(content)   #将servertpl.conf里面的所有内容写入到polls.conf，包括主机名的改变

    p.upload(os.path.join(config.base.Base_dir,'django_deploy','polls.conf'),'/usr/local/nginx1.10.2/conf/vhosts.d/polls.conf')
    p.cmd('chown -R nginx:nginx /projects')
    p.cmd('nginx -s reload')

if __name__ == '__main__':
    django_deploy()