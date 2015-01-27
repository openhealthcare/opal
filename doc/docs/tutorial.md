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
            templates/          # Your template directory
            migrations/         # Your Database migrations directory


## Test it out 

// TODO - should see a holding welcome page

## Enable lists 

// TODO - enable the lists module

// TODO - this is a good time to explain patients vs Episodes.

## Enable Lookuplists

// TODO - this is a good time to introduce the concept of FKorFT && Lookup lists.

## Add your own data models

So far we've begun to get a sense of the batteries-included parts of OPAL, 
but before long, you're going to need to create models for your own uniquely
beautiful snowflake of a use case. 

Let's see how that works by creating a TODO list model that is assigned to
episodes of care. In your `mynewapp/models.py` : 

    class TODOItem(models.EpisodeSubrecord):
        job       = fields.CharField(max_length=200)
        due_date  = fields.DateField(blank=True, null=True)
        details   = fields.TextField(blank=True, null=True)
        completed = fields.BooleanField(default=False)
          
This is simply a Django model, apart from the parent class `models.EpisodeSubrecord` 
which provides us with the relationship to individual episodes of care, and will also
create JSON APIs for creating & updating it, as well as ensuring that the OPAL js 
libraries know it exists.

Next, we're going to let OPAL take care of the boilerplate that we'll need to use this
model in our application. From the commandline: 

    $ opal scaffold mynewapp

Let's take a look at what that did: 

* It created a south migration (Migrations live in `mynewapp/migrations`)
* It created a detail template `mynewapp/templates/records/todo_item.html`
* It created a form template `mynewapp/templates/modals/todo_item_modal.html`

### Detail template

The default detail template simply displays each field on a new line, if it is set in your model:

    <span ng-show="item.job">[[ item.job ]] <br /></span>
    <span ng-show="item.due_date">[[ item.due_date  | shortDate ]] <br /></span>
    <span ng-show="item.details">[[ item.details ]] <br /></span>
    <span ng-show="item.completed">[[ item.completed ]] <br /></span>

### Form template

The default form template will display each field on a new line, wits some basic appropriate types set.
It uses the OPAL form helpers templatetag library.

    {% extends 'modal_base.html' %}
    {% load forms %}
    {% block modal_body %}
      <form class="form-horizontal">
       {% input  label="Job" model="editing.job"  %}
       {% datepicker  label="Due Date" model="editing.due_date"  %}
       {% textarea  label="Details" model="editing.details"  %}
       {% checkbox  label="Completed" model="editing.completed"  %}
      </form>
    {% endblock %}

### Adding it to our lists

Lists have schemas, which are defined by your application. 

Open mynewapp/schemas.py
