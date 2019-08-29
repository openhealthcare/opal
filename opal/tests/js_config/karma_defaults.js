module.exports = function(includedFiles, baseDir, coverageFiles){
    // includedFiles: The files to include in the karma conf
    // baseDir: The base directory of the module that you're using to run tests
    // coverageFiles: The files to run coverralls on, if no coverage
    // files are passed in, coverralls won't be used
    var useCoverage = !!coverageFiles;
    var browsers, coverageReporter, opalRoute;
    var basePath = __dirname + "/../../static/js";

    var OPAL_DEPENDENCIES = [
      "lib/bower_components/angular/angular.js",
      "lib/bower_components/angular-route/angular-route.js",
      "lib/bower_components/angular-resource/angular-resource.js",
      "lib/bower_components/angular-cookies/angular-cookies.js",
      "lib/bower_components/angular-mocks/angular-mocks.js",
      'lib/angular-ui-utils-0.1.0/ui-utils.js',
      "lib/ui-bootstrap-tpls-0.14.3.js",
      "lib/angulartics-0.17.2/angulartics.min.js",
      "lib/angulartics-0.17.2/angulartics-ga.min.js",
      'lib/ngprogress-lite/ngprogress-lite.js',
      'lib/jquery-1.11.3/jquery-1.11.3.js',
      'lib/utils/underscore.js',
      'lib/utils/showdown.js',
      'lib/utils/moment.js',
      'lib/utils/clipboard.js',
      'lib/bower_components/angular-growl-v2/build/angular-growl.js',
      "lib/bower_components/ng-idle/angular-idle.js",
      'lib/bower_components/angular-ui-select/dist/select.js',
      "lib/bower_components/angular-local-storage/dist/angular-local-storage.js",
      'opal/utils.js',
      'opal/opaldown.js',
      'opal/directives.js',
      'opal/filters.js',
      'opal/services_module.js',
      'opal/services/*.js',
      'opal/controllers_module.js',
      'opal/controllers/*.js',
      '../../core/pathway/static/js/pathway/**/*.js',
      '../../core/search/static/js/search/**/*.js',
      'test/test_helper.js'
    ];

    var preprocessors = {};

    coverageFiles.forEach(function(a){
      preprocessors[a] = 'coverage';
    });

    var FailFastReporter = function(){
      this.onSpecComplete = function (browser, result) {
        console.log('failfast oncomplete')
        if (result.success === false) {
          throw new Error(result.log);
        }
      }
    }

    var plugins = [
      "karma-coverage",
      "karma-jasmine",
      {
        'reporter:failfast': ['type', FailFastReporter]
      }
    ];

    if(process.env.TRAVIS){
        browsers = ["Firefox"];
        plugins.push("karma-firefox-launcher");
        plugins.push("karma-coveralls");
        if(useCoverage){
          coverageReporter = {
              type: 'lcovonly', // lcov or lcovonly are required for generating lcov.info files
              dir: baseDir + '/coverage/',
          };
        }
    }
    else{
        browsers = ['PhantomJS'];
        plugins.push("karma-phantomjs-launcher");
        if(useCoverage){
          coverageReporter = {
              type : 'html',
              dir : baseDir + '/htmlcov/js/'
          };
        }
    }

    var defaults = {
        frameworks: ['jasmine'],
        browsers: browsers,
        basePath:  basePath,
        files: OPAL_DEPENDENCIES.concat(includedFiles),
        // Stolen from http://oligofren.wordpress.com/2014/05/27/running-karma-tests-on-browserstack/
        browserDisconnectTimeout : 10000, // default 2000
        browserDisconnectTolerance : 1, // default 0
        browserNoActivityTimeout : 4*60*1000, //default 10000
        captureTimeout : 4*60*1000, //default 60000
        preprocessors: preprocessors,
        reporters: ['progress'],
        plugins: plugins,
    };

    if(useCoverage){
      defaults.reporters = ['progress', 'coverage'];
      defaults.coverageReporter = coverageReporter;
    }


    if(process.argv.indexOf('--failfast') != -1){
      defaults.reporters.push('failfast')
    }

  return defaults;

};
