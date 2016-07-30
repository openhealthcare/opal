"""
OPAL scaffolding and code generation
"""
import inspect
import os
import subprocess
import sys

from django.utils.crypto import get_random_string
import ffs
from ffs import nix
from ffs.contrib import mold

import opal

OPAL             = ffs.Path(opal.__file__).parent
SCAFFOLDING_BASE = OPAL/'scaffolding'
SCAFFOLD         = SCAFFOLDING_BASE/'scaffold'
PLUGIN_SCAFFOLD  = SCAFFOLDING_BASE/'plugin_scaffold'


def write(what):
    if 'runtests.py' in sys.argv:
        return
    sys.stdout.write("{0}\n".format(what))

# TODO: This is backported from Django 1.9.x - after we upgrade to target
# Django 1.9.x can we kill this and import it from there please.
def get_random_secret_key():
    """
    Return a 50 character random string usable as a SECRET_KEY setting value.
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(50, chars)

def interpolate_dir(directory, **context):
    """
    Recursively iterate through .jinja2 files below DIRECTORY, rendering them as
    files with CONTEXT.
    """
    # Frist, let's deal with files at our current level.
    for t in directory.ls('*.jinja2', all=True):
        realname = str(t[-1]).replace('.jinja2', '')
        target = t[:-1]/realname
        target << mold.cast(t, **context)
        os.remove(t)

    # OK. Now let's dive in.
    for t in directory.ls():
        if t.is_dir:
            interpolate_dir(t, **context)
    return

def _set_settings_module(name):
    os.environ['DJANGO_SETTINGS_MODULE'] = '{0}.settings'.format(name)
    if '.' not in sys.path:
        sys.path.append('.')
    import django
    django.setup()
    return


def startproject(args, USERLAND_HERE):
    """
    In which we perform the steps required to start a new OPAL project.

    1. Run Django' Startproject
    2. Create a data/lookuplists dir
    3. Copy across the scaffolding directory
    4. Interpolate our project data into the templates.
    5. Swap our scaffold app with the Django created app
    6. Interpolate the code templates from our scaffold app
    7. Create extra directories we need
    8. Run Django's migrations
    9. Create a superuser
    10. Initialise our git repo
    """
    name = args.name

    project_dir = USERLAND_HERE/name
    if project_dir:
        write("\n\nDirectory {0} already exists !".format(project_dir))
        write("Please remove it or choose a new name.\n\n")
        sys.exit(1)

    # 1. Run Django Startproject
    write("Creating project dir at {0}".format(project_dir))
    os.system('django-admin.py startproject {0}'.format(name))

    write("Bootstrapping your OPAL project...")

    # 2. Create empty directories
    lookuplists = project_dir/'data/lookuplists'
    lookuplists.mkdir()

    # 3. Copy across the scaffold
    with SCAFFOLD:
        for p in SCAFFOLD.ls():
            target = project_dir/p[-1]
            p.cp(target)

    # Dotfiles need their dot back
    gitignore = project_dir/'gitignore'
    gitignore.mv(project_dir/'.gitignore')


    # 3. Interpolate the project data
    interpolate_dir(project_dir, name=name, secret_key=get_random_secret_key())

    app_dir = project_dir/name

    # 5. Django Startproject creates some things - let's kill them &
    # replace with our own things.
    nix.rm(app_dir, recursive=True, force=True)
    nix.mv(project_dir/'app', app_dir)

    # 7. Create extra directories we need
    js = app_dir/'static/js/{0}'.format(name)
    css = app_dir/'static/css'
    js.mkdir()
    css.mkdir()
    nix.mv(app_dir/'static/js/app/routes.js', app_dir/'static/js/{0}/routes.js'.format(name))
    nix.mv(app_dir/'static/js/app/flow.js', app_dir/'static/js/{0}/flow.js'.format(name))

    templates = app_dir/'templates'/name
    templates.mkdir()

    assets = app_dir/'assets'
    assets.mkdir()
    assets_explainer = assets/'README.md'
    assets_explainer << """
    This placeholder file is here to ensure that there we still have our STATICFILES_DIRS target
    if we commit generated code to source control.

    This means that we can run collectstatic OK.
    """

    # We have this here because it uses name from above.
    def manage(command):
        args = ['python', '{0}/manage.py'.format(name)]
        args += command.split()
        args.append('--traceback')

        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError:
            sys.exit(1)
        return

    # 8. Run Django's migrations
    write( 'Creating Database')
    manage('makemigrations {0}'.format(name))
    manage('migrate')

    # 9. Create a superuser
    sys.path.append(os.path.join(os.path.abspath('.'), name))
    _set_settings_module(name)

    from django.contrib.auth.models import User
    user = User(username='super')
    user.set_password('super1')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    from opal.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.force_password_change = False
    profile.save()

    # 11. Initialise git repo
    os.system('cd {0}; git init'.format(name))


def _strip_non_user_fields(schema):
    exclude = ['created', 'updated', 'created_by_id', 'updated_by_id', 'consistency_token']
    return [f for f in schema if f['name'] not in exclude]


def _get_template_dir_from_record(record):
    """
    Given a RECORD, return it's relative template dir
    """
    modelsfile = inspect.getfile(record)
    if modelsfile.endswith('.pyc'):
        modelsfile = modelsfile.replace('.pyc', '.py')
    appdir = ffs.Path(modelsfile)[:-1]
    templates = appdir/'templates'
    return templates


def create_display_template_for(record, scaffold_base):
    """
    Create a display template for RECORD.
    """
    write('Creating display template for {0}'.format(record))
    name = record.get_api_name()

    # 1. Locate the records template directory
    templates = _get_template_dir_from_record(record)
    records = templates/'records'
    if not records:
        records.mkdir()

    display_template = scaffold_base/'record_templates/record_display.jinja2'
    template = records/'{0}.html'.format(name)
    fields = _strip_non_user_fields(record.build_field_schema())
    contents = mold.cast(display_template, record=record, fields=fields)
    # We often get lots of lines containing just spaces as a Jinja2 artifact. Lose them.
    contents = "\n".join(l for l in contents.split("\n") if l.strip())
    template << contents
    return

def create_form_template_for(record, scaffold_base):
    """
    Create a form template for RECORD.
    """
    write('Creating form template for{0}'.format(record))
    name = record.get_api_name()

    templates = _get_template_dir_from_record(record)
    forms = templates/'forms'
    if not forms:
        forms.mkdir()

    form_template = scaffold_base/'record_templates/record_form.jinja2'
    template = forms/'{0}_form.html'.format(name)
    fields = _strip_non_user_fields(record.build_field_schema())
    contents = mold.cast(form_template, record=record, fields=fields)
    # We often get lots of lines containing just spaces as a Jinja2 artifact. Lose them.
    contents = "\n".join(l for l in contents.split("\n") if l.strip())
    template << contents
    return
