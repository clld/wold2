from fabric.api import task, hosts

from clld.deploy import config, util


APP = config.APPS['wold2']


@hosts('forkel@cldbstest.eva.mpg.de')
@task
def deploy_test():
    util.deploy(APP, 'test')


@task
def deploy():
    util.deploy(APP, 'production')
