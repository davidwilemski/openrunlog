

from fabric.api import *
from fabtools import require
import fabtools
import os

PROJ_NAME = os.environ["VIRTUAL_ENV"].split('/')[-1]
VENV_DIR = '~/{}_env/'.format(PROJ_NAME)
PROJ_DIR = '~/{}/'.format(PROJ_NAME)

@task
def deploy():
    with prefix('source ' + VENV_DIR + 'bin/activate'):
        with cd(PROJ_DIR):
            run('git pull')
            fabtools.python.install_requirements(PROJ_DIR + 'requirements.txt')
            run('python setup.py install')
    restart()

@task
def start():
    with prefix('source ' + VENV_DIR + 'bin/activate'):
        with cd(PROJ_DIR):
            run('supervisord')

@task
def stop():
    with prefix('source ' + VENV_DIR + 'bin/activate'):
        with cd(PROJ_DIR):
            run('kill `cat supervisord.pid`')

@task
def restart():
    stop()
    start()

@task
def setup():
    require.python.pip()

    # Create venv
    run('virtualenv -p /usr/local/bin/python2.7 ' + PROJ_NAME + '_env')

    # activate venv
    with prefix('source ' + VENV_DIR + 'bin/activate'):
        # clone repo
        run('git clone https://github.com/davidwilemski/openrunlog.git ' + PROJ_NAME)
        
        # install requirements
        fabtools.python.install_requirements(PROJ_DIR + 'requirements.txt')

        with cd(PROJ_DIR):
            run('python setup.py install')

    start()
