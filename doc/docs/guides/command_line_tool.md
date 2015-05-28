# The OPAL Command line tool

OPAL ships with a helpful command line tool that helps with administrative tasks.

The `opal` script should be on your system path if you installed OPAL via setup.py or 
pip. You can check whether it is available by running this command: 

    $ opal -v

## Available Commands

### startproject &lt;name&gt;

Creates a new OPAL project.

This creates boilerplate and a default configuration for your new project, including
creating a new underlying Django project, updating default settings to be compatible
with OPAL, creating directories and code boilerplate, and running initial migrations.

### startplugin &lt;name&gt;

Creates boilerplate code, and directory structures for a new OPAL plugin.

### scaffold &lt;appname&gt;

Use with new record models.

Creates and runs automatic migrations, creates display and form (modal) templates.

### test &lt;what&gt;

Run our tests suites.

Defaults to running both Python and Javascript tests.

If specified, will only run one specific kind of test.

   $ opal test py
   $ opal test js

When running Python tests, the `-t` or `--test` option allows the user to specify a single
test module, case or method to run.

   $ opal test py -t opal.tests.test_models
