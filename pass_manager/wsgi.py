"""
WSGI config for pass_manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import sys

import site

site.addsitedir('/home/ubuntu/.local/lib/python3.6/site-packages')

sys.path.append('home/ubuntu/OneDrive/Pycharm/pass_manager')
sys.path.append('home/ubuntu/OneDrive/Pycharm/pass_manager/pass_manager')

print(sys.version)
print(sys.prefix)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pass_manager.settings')

from django.core.wsgi import get_wsgi_application
import pymysql
pymysql.install_as_MySQLdb()
application = get_wsgi_application()
