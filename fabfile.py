from fabric.api import task

from clld.deploy import config, util


APP = config.APPS['wold2']


@task
def deploy_test():
    util.deploy(APP, 'test')


@task
def deploy():
    util.deploy(APP, 'production')
