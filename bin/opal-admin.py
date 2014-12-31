#!/usr/bin/env python
"""
OPAL Admin script.
In which we expose useful commandline functionality to our users.
"""
import os
import sys

import ffs
from ffs import nix
from ffs.contrib import mold

USERLAND_HERE = ffs.Path('.').abspath
SCRIPT_HERE = ffs.Path(__file__).parent
SCAFFOLD = SCRIPT_HERE/'scaffold'

def interpolate_dir(directory, **context):
    """
    Iterate through .jinja2 files in DIRECTORY, rendering them as
    files with CONTEXT.
    """
    for t in directory.ls('*.jinja2'):
        realname = str(t[-1]).replace('.jinja2', '')
        target = t[:-1]/realname
        target << mold.cast(t, **context)
        t.rm()
    return

def startproject(name):
    """
    In which we perform the steps required to start a new OPAL project.
    
    1. Run Django' Startproject
    2. Copy across the scaffolding directory
    3. Interpolate our project data into the templates.
    4. Create a data/lookuplists dir
    5. Swap our scaffold app with the Django created app
    6. Interpolate the code templates from our scaffold app
    """
    project_dir = USERLAND_HERE/name
    print "Creating project dir at {0}".format(project_dir)
    os.system('django-admin.py startproject {0}'.format(name))

    print "Creating OPAL Scaffold"
    with SCAFFOLD:
        for p in SCAFFOLD.ls():
            target = project_dir/p[-1]
            p.cp(target)

    interpolate_dir(project_dir, name=name)
        
    lookuplists = project_dir/'data/lookuplists'
    lookuplists.mkdir()
    
    app_dir = project_dir/name
    #!!! TODO: THIS IS NOT HAPPENING!
    nix.rm(app_dir, force=True)
    # nix.mv(project_dir/'app', app_dir)

    # # !!! TODO: make this a reals secret key please!
    # interpolate_dir(project_dir, name=name, secret_key='foobarbaz')
    

    return


def create_plugin():
    """
    The steps to create our plugin are: 

    * Create a top level directory (from sys.argv)
    * Create a setup.py
    * Create a readme
    * Create a license
    * Create the raw subfiles 
      - __init__.py with plugin subclass
      - static directory
      - templates directory
    * Drop in default .gitignore
    """
    target_dir = sys.argv[-1]
    root = ffs.Path(target_dir)
    root.mkdir()
    codename = str(root[-1]).replace('opal-', '')
    code_root = root/codename
    code_root.mkdir()
    init = code_root/'__init__.py'
    init.touch()
    templates = code_root/'templates'
    templates.mkdir()
    static = code_root/'static'
    return

def main():
    name = sys.argv[-1]
    startproject(name)
    sys.exit(0)

if __name__ == '__main__':
    main()
