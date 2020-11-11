# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import idaapi

def detect_env():
    """
    Detect and load a Python virtual environment if present.
    """
    print("Detecting python virtual environment...")

    try:
        path = activate_virtualenv_env(None, False)
        print(" - Virtualenv activated: %s" % path)
        return True
    except ValueError as e:
        print(" - Virtualenv: %s" % e)

    try:
        path = activate_conda_env(None, None, False)
        print(" - Conda env activated: %s" % path)
        return True
    except ValueError as e:
        print(" - Conda: %s" % e)

    return False

def activate_virtualenv_env(virtualenv=None, interactive=True):
    """
    Activate a Virtualenv based virtual environment.
    """
    folder = "Scripts" if os.name == "nt" else "bin"

    if virtualenv == None:
        virtualenv = os.environ.get("VIRTUAL_ENV")

        if not virtualenv and interactive:
            default_virtualenv = os.path.join(idaapi.get_user_idadir(), "virtualenv")
            virtualenv = idaapi.askstr(0, default_virtualenv, "Select a virtualenv")

    if not virtualenv:
        raise ValueError("No active virtualenv")

    if not os.path.isdir(virtualenv):
        raise ValueError("This path is not a dir: " + virtualenv)

    virtualenv_script = os.path.join(virtualenv, folder, "activate_this.py")
    if not os.path.isfile(virtualenv_script):
        raise ValueError('Enable to find "' + folder + os.sep + 'activate_this.py" in virtualenv: ' + virtualenv)

    with open(virtualenv_script) as infile:
        exec(infile.read(), dict(__file__=virtualenv_script))

    return virtualenv

def activate_conda_env(base=None, env=None, interactive=True):
    """
    Activate a Conda based virtual environment.
    """
    folder = "Scripts" if os.name == "nt" else "bin"

    # Get env
    if env == None:
        env = os.environ.get("CONDA_PREFIX")
        if not env and interactive:
            root_path = os.path.abspath(os.sep)
            env = idaapi.askstr(0, root_path, "Select a env")

    # Check env
    if not env:
        raise ValueError("No active Conda env")
    if not os.path.isdir(env):
        raise ValueError("This path is not a dir: " + env)

    ###
    # Based on the virtualenv script 'activate_this.py'
    ###

    # Patch PATH
    old_os_path = os.environ['PATH']
    os.environ['PATH'] = env + os.pathsep + os.path.join(env, folder) + os.pathsep + old_os_path

    # Compose new system path
    if sys.platform == 'win32':
        site_packages = os.path.join(env, 'Lib', 'site-packages')
    else:
        site_packages = os.path.join(env, 'lib', 'python%s' % sys.version[:3], 'site-packages')

    # Patch system path
    prev_sys_path = list(sys.path)
    import site
    site.addsitedir(site_packages)
    sys.real_prefix = sys.prefix
    sys.prefix = env

    # Move the added items to the front of the path:
    new_sys_path = []
    for item in list(sys.path):
        if item not in prev_sys_path:
            new_sys_path.append(item)
            sys.path.remove(item)
    sys.path[:0] = new_sys_path

    return env

# make the env activation functions accessible to the IDA console (7.0+)
sys.modules["__main__"].activate_virtualenv_env = activate_virtualenv_env
sys.modules["__main__"].activate_conda_env = activate_conda_env