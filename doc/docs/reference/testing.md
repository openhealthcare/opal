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

### Installing javascript testing tools

To installing Karma, Jasmine and Phantomjs in a local directory:

```bash
npm install jasmine-core karma karma-coverage karma-jasmine karma-phantomjs-launcher
```

### Setting up the karma environment for your application

If you'd like to run karma tests, Opal ships with a function to give you a default karma config.

In your karma config just `require('[[ path to opal ]]/config/karma_defaults.js')`

The function takes in the files you want to include and runs karma tests on them.

```js
// config/karma.config.js

module.exports = function(config){
  var opalPath = '../../opal';

  var karmaDefaults = require(opalPath + '/config/karma_defaults.js');
  var baseDir = __dirname + '/..';
  var includedFiles = [
     ...
  ];

  var defaultConfig = karmaDefaults(includedFiles, baseDir);
  config.set(defaultConfig);
};
```

If run from opal test js, we set the path to opal as an env variable called
OPAL_LOCATION

## Test Coverage

The Opal test runner has a `-c` option which runs coverage reports for both Python and Javascript code:

```bash
opal test -c
```

Python test coverage uses the `coverage` tool and you may want to set include/excludes in a `.coveragerc`.

Javascript test files to be reported on should be passed as an extra argument to `karmaDefaults`:

```js
  var coverageFiles = [
     ...
  ];
  var defaultConfig = karmaDefaults(includedFiles, baseDir, coverageFiles);
```

HTML test coverage reports will be output to the directory `htmlcov` and `htmlcov/js` at the root of your application.
