from __future__ import with_statement
import os

from fabric.api import task
from fabric.contrib.project import rsync_project
from fabric.operations import run
from fabric.contrib.files import exists

project_name = 'golfstats'
short_project_name = 'golfstats'

root_dir = os.path.join('/opt', short_project_name)
log_dir = '/var/log/%s' % project_name
virtual_environment_dir = os.path.join(root_dir, 'venv')
deployment_temp_dir = os.path.join(root_dir, 'deployment-temp')
deployments_dir = os.path.join(root_dir, 'deployments')
app_dir = os.path.join(root_dir, 'app')
app_src_dir = os.path.join(app_dir, 'src', project_name)
python_path = os.path.join(virtual_environment_dir, 'bin/python')
pip_path = os.path.join(virtual_environment_dir, 'bin/pip')

variables = {
    'project_name': project_name,
    'root_dir': root_dir,
    'log_dir': log_dir,
    'deployment_temp_dir': deployment_temp_dir,
    'deployments_dir': deployments_dir,
    'virtual_environment_dir': virtual_environment_dir,
    'pip_path': pip_path,
    'app_dir': app_dir,
    'app_src_dir': app_src_dir
}


@task(alias="bare-metal-init")
def bare_metal_init():
    """
    Usually run as root
    """
    run("apt-get update")
    run("apt-get -y dist-upgrade")
    run("apt-get -y install subversion ntpdate ntp build-essential python-software-properties supervisor rsync sudo")

    #run('deluser --quiet %(project_name)s' % vars)
    run('adduser --home %(root_dir)s --disabled-password --quiet --gecos "" %(project_name)s' % variables,
        warn_only=True)

    run('rm -Rf %(root_dir)s' % variables)
    run("mkdir -p %(deployments_dir)s" % variables)
    run("mkdir -p %(virtual_environment_dir)s" % variables)
    run("mkdir -p %(log_dir)s" % variables)

    run("apt-get -y install python-dev build-essential python-pip rsync ntp")
    run("apt-get -y build-dep psycopg2 gettext lxml python-numpy")

    run("pip install pip==1.3.1 virtualenv")

    run("virtualenv %(virtual_environment_dir)s" % variables)

    run("chown --recursive %(project_name)s:%(project_name)s %(root_dir)s" % variables)
    run("chown --recursive %(project_name)s:%(project_name)s %(log_dir)s" % variables)


@task
def deploy(package_name, settings, build_id):
    i_path = os.path.join(os.path.dirname(__file__), '..', )
    rsync_project(deployment_temp_dir, local_dir=i_path, exclude=['.git', '.svn', '.idea', 'venv', '*.pyc'],
                  delete=True)

    source_dir = os.path.join(deployments_dir, package_name)
    if exists(source_dir):
        run('rm -rf %s' % source_dir)

    variables.update(
        {
            'deployment_dir': source_dir,
            'settings': settings,
            'build_id': build_id
        }
    )

    run('cp -r %(deployment_temp_dir)s %(deployment_dir)s' % variables)

    run('ln -nsf %(deployment_dir)s %(app_dir)s' % variables)

    run('%(pip_path)s install -r %(app_dir)s/requirements.txt' % variables)

    run(
        'find %(deployments_dir)s -maxdepth 1 -type d -name "release-*" | sort -r -n | tail -n +20 | xargs -I %% rm --recursive --force %%' % variables)

    run('echo "REVISION=\'%(build_id)s\'" > %(app_src_dir)s/revision.py' % variables)
    run('echo "RELEASE_TYPE=\'%(settings)s\'" > %(app_src_dir)s/master_config.py' % variables)

    dev_file = os.path.join(app_src_dir, 'developer.py')
    if exists(dev_file):
        print 'DEV FILE EXISTS'
        run('rm %s' % dev_file)

    run('touch %(app_dir)s/reload' % variables)


@task
def restart_supervisor(program):
    # requires 'golfstats ALL=(ALL) NOPASSWD: /usr/bin/supervisorctl*'
    run('sudo /usr/bin/supervisorctl restart %s' % program)