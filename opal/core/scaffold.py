"""
OPAL scaffolding and code generation
"""
import inspect
import sys

import ffs
from ffs.contrib import mold

def write(what):
    if 'runtests.py' in sys.argv:
        return
    sys.stdout.write("{0}\n".format(what))

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
