## The Opal development environment

### Getting the code

If you're planning on working on Opal we recommend installing in a Virtualenv - to make that
easy, we would suggest installing Virtualenvwrapper. To obtain the code, set up a virtualenv
and install Opal and the dependencies you'll need, run the following:

```bash
git clone git@github.com:openhealthcare/opal
cd opal
mkvirtualenv -a $PWD opal
python setup.py develop
pip install -r test-requirements.txt
```

### Running the tests

In order to run the Opal test suite you'll also need to install the Javascript test runner:

```bash
npm install jasmine-core karma karma-coverage karma-jasmine karma-phantomjs-launcher
```

To run the test suite:

```bash
opal test
```

You can also run just one suite (Javascript or Python) individually:

```bash
opal test py
opal test js
```
