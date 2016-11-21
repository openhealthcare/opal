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
    var additionalDependencies = require('./karma_dependencies.js');

    config.set({
        frameworks: ['jasmine'],
        browsers: browsers,
        basePath:  basePath,

        files: additionalDependencies().concat([
            //JASMINE,
            //JASMINE_ADAPTER,
            'opal/app.js',
            'opal/routes.js',
            '../../core/search/static/js/search/controllers/*',
            '../../core/search/static/js/search/services/*',
            'opaltest/*.js',
        ]),

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
