## Automated Testing

Built on top of Django and Angular, Opal applications have great support for automated testing.

Opal provides some utilities to make testing your application even easier.

## Command Line test runner

The `opal` command line tool has a `test` command which will run unittests for both the server and client
side components of your application.

## Javascript testing

By default, we recommend using Jasmine and Karma to test your javascript code.  
<blockquote><small>
Of course you can use any test framework you choose, although Opal doesn't currently ship with helpers 
for any other frameworks.
</small></blockquote>


### Setting up the karma environment for your application

If you'd like to run karma tests, OPAL ships with a function to give you a default karma config.

In your karma config just `require('[[ path to opal ]]/config/karma_defaults.js')`

The function takes in the files you want to include and runs karma tests on them.

If you want to run coverage tests, pass in the base directory your application and the files you want to run coverage on.

locally this will put a at the base directory of your application + '../../htmlcov/js/'.

On travis it would put it on at the base directory of your application + '/coverage'
