# Deploying Opal

It's no use building a great application if you can't easily deploy it.

Because Opal is built on top of Django, we can take advantage of all the hard work that
[the open source community](https://docs.djangoproject.com/en/1.10/howto/deployment/) has
put into making it easy to deploy Django applications.

Opal can be deployed on any modern web server, if you're new to deploying Django applications
we'd recommend you try [Apache and mod_wsgi](https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/modwsgi/)
first. In most cases it'll be the easiest deployment choice.

## Heroku

The Opal scaffold application comes with a `Procfile` ready for Heroku deployment, and the
default `requirements.txt` includes some dependencies that allow us to easily deploy to
Heroku.

(Other PaaS and cloud technologies are available, and Opal should deploy fairly easliy
to any of them!)

### Deploying to Heroku

Firstly, [sign up for Heroku](https://signup.heroku.com/), and install their
[command line tool](https://devcenter.heroku.com/articles/heroku-cli).

We then need to create a new heroku application, and set up our database:

```bash
heroku create
heroku addons:create heroku-postgresql
```

Next, we need to push our application code to the Heroku server with git:

```bash
git push heroku master
```

Then we can run our migrations, load our lookuplists and create a user:

```bash
heroku run python manage.py migrate
heroku run python manage.py load_lookup_lists
heroku run python manage.py createsuperuser
```

We should now be able to log in to our deployed app - to open it in a browser:

```bash
heroku open
```
