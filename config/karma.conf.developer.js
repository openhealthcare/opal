module.exports = function(config){
    config.set({
        frameworks: ['jasmine'],
        browsers: ['Firefox'],
        basePath:  '/usr/lib/ohc/opal/opal/static/js',

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

            'angular-strap-2.0.3/modules/tooltip.js',
            'angular-strap-2.0.3/modules/tooltip.tpl.js',
            'angular-strap-2.0.3/modules/dimensions.js',
            'angular-strap-2.0.3/modules/parse-options.js',
            'angular-strap-2.0.3/modules/date-parser.js',
            'angular-strap-2.0.3/modules/datepicker.js',
            'angular-strap-2.0.3/modules/datepicker.tpl.js',
            'angular-strap-2.0.3/modules/timepicker.js',
            'angular-strap-2.0.3/modules/timepicker.tpl.js',
            'angular-strap-2.0.3/modules/typeahead.js',
            'angular-strap-2.0.3/modules/typeahead.tpl.js',
            'ngprogress-lite/ngprogress-lite.js',
            'jquery-1.11.0/jquery.js',
            'utils/underscore.js',
            'utils/moment.js',
            'bower_components/angular-growl-v2/build/angular-growl.js',
            'bower_components/ment.io/dist/mentio.js',
            'bower_components/ment.io/dist/templates.js',

            'opal/utils.js',
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

    })
}
