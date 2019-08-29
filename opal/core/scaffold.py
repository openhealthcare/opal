"""
Opal scaffolding and code generation
"""
import inspect
import errno
import os
import subprocess
import sys

from django.core import management
from django.utils.crypto import get_random_string
from django.apps import apps
from opal.core import subrecords
import ffs
from ffs import nix
from ffs.contrib import mold

import opal
from opal.utils import write

OPAL             = ffs.Path(opal.__file__).parent
SCAFFOLDING_BASE = OPAL/'scaffolding'
SCAFFOLD         = SCAFFOLDING_BASE/'scaffold'
PLUGIN_SCAFFOLD  = SCAFFOLDING_BASE/'plugin_scaffold'


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
    Recursively iterate through .jinja2 files below DIRECTORY, rendering them
    as files with CONTEXT.
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


def create_lookuplists(root_dir):
    lookuplists_dir = root_dir/'data/lookuplists'
    lookuplists_dir.mkdir()


def call(cmd, **kwargs):
    """
    Call an external program in a subprocess
    """
    write("Calling: {}".format(' '.join(cmd)))
    try:
        subprocess.check_call(cmd, **kwargs)
    except subprocess.CalledProcessError:
        write("Failed to run: {}".format(' '.join(cmd)))
        sys.exit(1)


def call_if_exists(cmd, failure_message, **kwargs):
    """
    Call an external program in a subprocess if it exists.

    Returns True.

    If it does not exist, write a failure message and return False
    without raising an exception
    """
    try:
        call(cmd, **kwargs)
        return True
    except OSError as e:
        if e.errno == errno.ENOENT:
            write(failure_message)
            return False
        else:
            raise


def start_plugin(name, USERLAND):
    name = name

    write('Bootstrapping "{0}" - your new Opal plugin...'.format(name))

    if 'opal' in name:
        reponame = name
        name = name.replace('opal-', '')
    else:
        reponame = 'opal-{0}'.format(name)

    root = USERLAND/reponame

    # 1. Copy across scaffold
    nix.cp_r(PLUGIN_SCAFFOLD, root)

    # 2n. Interpolate scaffold
    interpolate_dir(root, name=name, version=opal.__version__)

    # 3. Rename the code dir
    code_root = root/name
    nix.mv(root/'app', code_root)

    # 4. Create some extra directories.
    create_lookuplists(code_root)
    templates = code_root/'templates'
    templates.mkdir()
    static = code_root/'static'
    static.mkdir()
    jsdir = static/'js/{0}'.format(name)
    jsdir.mkdir()
    cssdir = static/'css'
    cssdir.mkdir()
    controllers = jsdir/'controllers'
    controllers.mkdir()
    services = jsdir/'services'
    services.mkdir()
    # 5. Initialize git repo
    call_if_exists(
        ('git', 'init'),
        'Unable to locate git; Skipping git repository initialization.',
        cwd=root, stdout=subprocess.PIPE
    )

    write('Plugin complete at {0}'.format(reponame))
    return


def scaffold_subrecords(
    app, migrations=True, dry_run=False, dir=SCAFFOLDING_BASE
):
    """
    In which we scaffold an django app (opal plugin or application).

    1. Make migrations
    2. Migrate
    3. Create Form Templates of all subrecords in the models
    4. Create Record Templates of all subrecords in the models
    """
    if app not in apps.all_models:
        err = "Unable to find app {} in settings.INSTALLED_APPS"
        raise ValueError(
            err.format(app)
        )

    if migrations:
        if dry_run:
            management.call_command(
                'makemigrations', app, "--traceback", "--dry-run"
            )
        else:
            management.call_command(
                'makemigrations', app, "--traceback"
            )
            management.call_command('migrate', app, "--traceback")

    models = apps.all_models[app]
    all_subrecords = set(i for i in subrecords.subrecords())

    for model in models.values():
        if model in all_subrecords:
            if not model.get_display_template():
                if dry_run:
                    write('No Display template for {0}'.format(model))
                else:
                    create_display_template_for(
                        model, SCAFFOLDING_BASE
                    )
            if not model.get_form_template():
                if dry_run:
                    write('No Form template for {0}'.format(model))
                else:
                    create_form_template_for(
                        model, SCAFFOLDING_BASE
                    )


def start_project(name, USERLAND_HERE):
    """
    In which we perform the steps required to start a new Opal project.

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
    11. Load referencedata shipped with Opal
    """

    project_dir = USERLAND_HERE/name
    if project_dir:
        write("\n\nDirectory {0} already exists !".format(project_dir))
        write("Please remove it or choose a new name.\n\n")
        sys.exit(1)

    write("Bootstrapping your Opal project...")

    # 1. Run Django Startproject
    write("Creating project dir at {0}".format(project_dir))
    project_dir.mkdir()
    management.call_command('startproject', name, project_dir)

    # 3. Copy across the scaffold
    with SCAFFOLD:
        for p in SCAFFOLD.ls():
            target = project_dir/p[-1]
            p.cp(target)

    # Dotfiles need their dot back
    gitignore = project_dir/'gitignore'
    gitignore.mv(project_dir/'.gitignore')

    # 4. Interpolate the project data
    interpolate_dir(project_dir, name=name, secret_key=get_random_secret_key(),
                    version=opal.__version__)

    app_dir = project_dir/name

    # 5. Django Startproject creates some things - let's kill them &
    # replace with our own things.
    nix.rm(app_dir, recursive=True, force=True)
    nix.mv(project_dir/'app', app_dir)

    #  7. Create extra directories we need
    js = app_dir/'static/js/{0}'.format(name)
    css = app_dir/'static/css'
    js.mkdir()
    css.mkdir()
    nix.mv(app_dir/'static/js/app/routes.js',
           app_dir/'static/js/{0}/routes.js'.format(name))
    os.rmdir(str(app_dir/'static/js/app'))

    templates = app_dir/'templates'/name
    templates.mkdir()

    assets = app_dir/'assets'
    assets.mkdir()
    assets_explainer = assets/'README.md'
    assets_explainer << """
    This placeholder file is here to ensure that there we still have our
    STATICFILES_DIRS target if we commit generated code to source control.

    This means that we can run collectstatic OK.
    """

    # 2. Create lookup lists
    create_lookuplists(app_dir)

    # We have this here because it uses name from above.
    def manage(command):
        args = ['python', os.path.join(name, 'manage.py')]
        args += command.split()
        args.append('--traceback')
        call(args)

    # 8. Run Django's migrations
    write('Creating Database')
    manage('makemigrations {0}'.format(name))
    manage('migrate')

    # 9. Create a superuser
    write('Creating superuser')
    manage('createopalsuperuser')

    # 10. Initialise git repo
    call_if_exists(
        ('git', 'init'),
        'Unable to locate git; Skipping git repository initialization.',
        cwd=project_dir, stdout=subprocess.PIPE
    )

    # 11. Load referencedata shipped with Opal
    manage('load_lookup_lists')


def _strip_non_user_fields(schema):
    exclude = [
        'created', 'updated', 'created_by_id',
        'updated_by_id', 'consistency_token'
    ]
    return [f for f in schema if f['name'] not in exclude]


def _get_template_dir_from_record(record):
    """
    Given a RECORD, return it's relative template dir
    """
    modelsfile = inspect.getfile(record)
    if modelsfile.endswith('.pyc'):
        modelsfile = modelsfile.replace('.pyc', '.py')

    appdir = None
    if modelsfile.endswith('models.py'):
        # We're assuming the app in question has models in
        # ./app/models.py
        appdir = ffs.Path(modelsfile)[:-1]
    else:
        if ffs.Path(modelsfile)[-2] == 'models':
            # We're assuming the app in question has models
            # in ./app/models/here.py
            appdir = ffs.Path(modelsfile)[:-2]

    if appdir is None:
        write("\n\nCripes!\n")
        write("We can't figure out what the correct directory to \n")
        write("put templates for {0} is :( \n\n".format(record))
        sys.exit(1)
    else:
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
    # We often get lots of lines containing just spaces as a Jinja2
    # artifact. Lose them.
    contents = "\n".join(l for l in contents.split("\n") if l.strip())
    template << contents
    return


def create_form_template_for(record, scaffold_base):
    """
    Create a form template for RECORD.
    """
    write('Creating form template for {0}'.format(record))
    name = record.get_api_name()

    templates = _get_template_dir_from_record(record)
    forms = templates/'forms'
    if not forms:
        forms.mkdir()

    form_template = scaffold_base/'record_templates/record_form.jinja2'
    template = forms/'{0}_form.html'.format(name)
    fields = _strip_non_user_fields(record.build_field_schema())
    contents = mold.cast(form_template, record=record, fields=fields)
    # We often get lots of lines containing just spaces as a Jinja2
    # artifact. Lose them.
    contents = "\n".join(l for l in contents.split("\n") if l.strip())
    template << contents
    return
