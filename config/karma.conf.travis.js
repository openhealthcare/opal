module.exports = function(config){
    config.set({
        frameworks: ['jasmine'],
        browsers: ['Firefox'],
        basePath:  __dirname + '/../opal/static/js',

        files: [
            //JASMINE,
            //JASMINE_ADAPTER,
            'angular-1.2.20/angular.js',
            'angular-1.2.20/angular-route.js',
            'angular-1.2.20/angular-resource.js',
            'angular-1.2.20/angular-cookies.js',
            'angular-1.2.20/angular-mocks.js',

            'angular-ui-utils-0.1.0/ui-utils.js',
            'angular-ui-bootstrap-0.10.0/ui-bootstrap-tpls.js',
            'angular-strap-2.3.1/angular-strap.js',
            'angular-strap-2.3.1/modules/compiler.js',
            'angular-strap-2.3.1/modules/tooltip.js',
            'angular-strap-2.3.1/modules/tooltip.tpl.js',
            'angular-strap-2.3.1/modules/dimensions.js',
            'angular-strap-2.3.1/modules/parse-options.js',
            'angular-strap-2.3.1/modules/date-parser.js',
            'angular-strap-2.3.1/modules/datepicker.js',
            'angular-strap-2.3.1/modules/datepicker.tpl.js',
            'angular-strap-2.3.1/modules/timepicker.js',
            'angular-strap-2.3.1/modules/timepicker.tpl.js',
            'angular-strap-2.3.1/modules/typeahead.js',
            'angular-strap-2.3.1/modules/typeahead.tpl.js',
            "angulartics-0.17.2/angulartics.min.js",
            "angulartics-0.17.2/angulartics-ga.min.js",
            'ngprogress-lite/ngprogress-lite.js',
            'jquery-1.11.3/jquery-1.11.3.js',
            'utils/underscore.js',
            'utils/moment.js',
            'utils/showdown.js',
            'bower_components/angular-growl-v2/build/angular-growl.js',
            'bower_components/ment.io/dist/mentio.js',
            'bower_components/ment.io/dist/templates.js',
            'bower_components/angular-ui-select/dist/select.js',
            "bower_components/angular-local-storage/dist/angular-local-storage.js",
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
        coverageReporter: {
            type: 'lcovonly', // lcov or lcovonly are required for generating lcov.info files
            dir: '../../../coverage/',
        }

    })
}
