# Writing your first OPAL App

This tutorial walks you through the creation of a clinical TODO list application. 

Because everyone needs TODO lists, & because you'll remember how it felt in the other
3 million TODO list application tutorials you've probably been doing.

We assume that you've already [Installed OPAL](installation.md). You can tell which version of opal is installed 
by running this command

    $ opal --version

## Bootstrapping a new project

To start a new OPAL project, we can bootstrap you the initial project structure, including
a Djano project, some core datamodels (complete with JSON APIs) and a general application structure.

From the commandline: 

    $ opal startproject mynewapp

This will create a mynewap directory where your new project lives. 

Let's have a look at what that created for you:


    mynewapp/                   # Your project directory
        LICENSE                 # A dummy LICENSE file
        Procfile                # A procfile ready for deployment to e.g. Heroku
        README.md
        manage.py               # Django's manage.py script
        requirements.txt        # Requirements file ready for your project
        
        data/                   # A dummy directory for fixtures
            lookuplists
        
        mynewapp/               # The actual python package for your application
             __init__.py
            flow.py             # How patients move through your services
            models.py           # Data models for your application 
            schema.py           # The list schemas for your application
            settings.py         # Helpfully tweaked Django settings
            tests.py            # Dummy unittests
            urls.py             # Django Urlconf
            wsgi.py             

            assets/             # Your static files directory
                css
                js

            templates/          # Your template directory
                mynewapp

            migrations/         # Your Database migrations directory
                __init__.py
                0001_initial.py

