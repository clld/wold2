from fabric.api import task, sudo
from fabtools import require
from fabtools.python import virtualenv


VENV = '/usr/local/venvs/wold2'


@task
def deploy():
    require.users.user('wold2', password='')
    require.postgres.user('wold2', 'wold2')
    require.postgres.database('wold2', 'wold2')
    require.files.directory(VENV, use_sudo=True)
    require.python.virtualenv(VENV)    

    require.files.directory('/var/log/wold2', use_sudo=True)

    with virtualenv(VENV):
        require.python.package('gunicorn')
        sudo('pip install -e git+git://github.com/clld/clld.git#egg=clld')
        sudo('pip install -e git+git://github.com/clld/wold2.git#egg=wold2')

