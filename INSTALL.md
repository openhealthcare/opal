OPAL - How to get it started version
======

* Standard Python Django Conventions Apply.
* If you're surprised by anything, re-read this document.
* Slower this time.

Do this once:
=========

```bash
sudo apt-get install python-dev postgresql-server-dev-9.1 virtualenvwrapper

TODO: Update these to reflect the new "Appy" status of this code.

git clone git@github.com:openhealthcare/opal
cd opal
mkvirtualenv -a $PWD opal
pip install -r requirements.txt
python manage.py syncdb --all
python manage.py migrate --fake
python manage.py loaddata dumps/options.json
python manage.py createinitialrevisions
```
