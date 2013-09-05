module.exports =  function(config){
    config.set({
        frameworks: ['jasmine'],
        browsers: ['Chrome'],
        basePath:  '../opal/assets/js',

        files: [
            //JASMINE,
            //JASMINE_ADAPTER,
            'angular-1.1.5/angular.js',
            'angular-1.1.5/angular-resource.js',
            'angular-1.1.5/angular-cookies.js',
            'angular-1.1.5/angular-mocks.js',
            'angular-1.1.5/angular-mocks.js',
            'angular-ui-utils-0.0.4/ui-utils.js',
            'angular-ui-bootstrap-0.4.0/ui-bootstrap-tpls.js',
            'angular-strap-0.7.5/angular-strap.js',
            'utils/underscore.js',
            'utils/moment.js',
            'opal/directives.js',
            'opal/filters.js',
            'opal/services.js',
            'opal/controllers.js',
            'opal/app.js',
            'opaltest/*.js'
        ],
        autoWatch: true,
    })
}
