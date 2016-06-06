module.exports = function(config){
    var browsers, basePath, coverageReporter;

    if(process.env.TRAVIS){
        browsers = ["Firefox"];
        coverageReporter = {
            type: 'lcovonly', // lcov or lcovonly are required for generating lcov.info files
            dir: '../../../coverage/',
        };
    }
    else{
        browsers = ['PhantomJS'];
        coverageReporter = {
            type : 'html',
            dir : '../../../htmlcov/js/'
        };
    }

    basePath = '../../opal/opal/static/js';

    config.set({
        frameworks: ['jasmine'],
        browsers: browsers,
        basePath:  basePath,

        files: [
            //JASMINE,
            //JASMINE_ADAPTER,

            "lib/bower_components/angular/angular.js",
            "lib/bower_components/angular-route/angular-route.js",
            "lib/bower_components/angular-resource/angular-resource.js",
            "lib/bower_components/angular-cookies/angular-cookies.js",
            "lib/bower_components/angular-mocks/angular-mocks.js",

            'lib/angular-ui-utils-0.1.0/ui-utils.js',
            'lib/angular-ui-bootstrap-0.10.0/ui-bootstrap-tpls.js',
            'lib/angular-strap-2.3.1/angular-strap.js',
            'lib/angular-strap-2.3.1/modules/compiler.js',
            'lib/angular-strap-2.3.1/modules/tooltip.js',
            'lib/angular-strap-2.3.1/modules/tooltip.tpl.js',
            'lib/angular-strap-2.3.1/modules/dimensions.js',
            'lib/angular-strap-2.3.1/modules/parse-options.js',
            'lib/angular-strap-2.3.1/modules/date-parser.js',
            'lib/angular-strap-2.3.1/modules/datepicker.js',
            'lib/angular-strap-2.3.1/modules/datepicker.tpl.js',
            'lib/angular-strap-2.3.1/modules/timepicker.js',
            'lib/angular-strap-2.3.1/modules/timepicker.tpl.js',
            'lib/angular-strap-2.3.1/modules/typeahead.js',
            'lib/angular-strap-2.3.1/modules/typeahead.tpl.js',
            "lib/angulartics-0.17.2/angulartics.min.js",
            "lib/angulartics-0.17.2/angulartics-ga.min.js",
            'lib/ngprogress-lite/ngprogress-lite.js',
            'lib/jquery-1.11.3/jquery-1.11.3.js',
            'lib/utils/underscore.js',
            'lib/utils/showdown.js',
            'lib/utils/moment.js',
            'lib/bower_components/angular-growl-v2/build/angular-growl.js',
            'lib/bower_components/ment.io/dist/mentio.js',
            'lib/bower_components/ment.io/dist/templates.js',
            'lib/bower_components/angular-ui-select/dist/select.js',
            "lib/bower_components/angular-local-storage/dist/angular-local-storage.js",
            'opal/utils.js',
            'opal/opaldown.js',
            'opal/directives.js',
            'opal/filters.js',
            'opal/services_module.js',
            'opal/services/*.js',
            'opal/services/flow.js',
            'opal/controllers_module.js',
            'opal/controllers/*.js',
            'opal/app.js',
            '../../core/search/static/js/search/controllers/*',
            '../../core/search/static/js/search/services/*',
            'opaltest/*.js',
        ],

        // Stolen from http://oligofren.wordpress.com/2014/05/27/running-karma-tests-on-browserstack/
        browserDisconnectTimeout : 10000, // default 2000
        browserDisconnectTolerance : 1, // default 0
        browserNoActivityTimeout : 4*60*1000, //default 10000
        captureTimeout : 4*60*1000, //default 60000
        preprocessors: {
            'opal/**/*.js': 'coverage',
            '../../core/search/static/js/search/**/*.js': 'coverage',
        },
        reporters: ['progress', 'coverage'],
        coverageReporter: coverageReporter
    })
}
