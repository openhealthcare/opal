var OPAL = {};
if(undefined === version){
    var version = 'test';
}
try { angular.module("opal.config") } catch(err) { /* failed to require */ angular.module('opal.config', [])}

OPAL.module = function(namespace, dependencies){
    dependencies = dependencies || [];

    var OPAL_ANGULAR_DEPS = window.OPAL_ANGULAR_DEPS;

    if(OPAL_ANGULAR_DEPS === undefined){
        OPAL_ANGULAR_DEPS = [];
    }

    var implicit_dependencies = [
        'angular-growl',
        'ngCookies',
        'angulartics',
        'angulartics.google.analytics',
        'LocalStorageModule',
    ];

    _.each(implicit_dependencies, function(dependency){
        if(!_.contains(dependencies, dependency)){
            dependencies.push(dependency);
        }
    });


    this.tracking = {
      manualTrack: window.OPAL_ANGULAR_EXCLUDE_TRACKING_PREFIX || window.OPAL_ANGULAR_EXCLUDE_TRACKING_QS,
      opal_angular_exclude_tracking_prefix: window.OPAL_ANGULAR_EXCLUDE_TRACKING_PREFIX || [],
      opal_angular_exclude_tracking_qs: window.OPAL_ANGULAR_EXCLUDE_TRACKING_QS || []
    };

    _.each(OPAL_ANGULAR_DEPS, function(d){
        dependencies.push(d);
    });

    var mod = angular.module(namespace, dependencies);

    if(this.tracking.manualTrack){
      mod.config(function($analyticsProvider) {
          $analyticsProvider.virtualPageviews(false);
      });
    }

    mod.config(function($cookiesProvider) {
        var future = new Date();
        future.setFullYear(future.getFullYear() + 1);
        $cookiesProvider.defaults.expires = future;
    });

    // See http://stackoverflow.com/questions/8302928/angularjs-with-django-conflicting-template-tags
    mod.config(function($interpolateProvider) {
	    $interpolateProvider.startSymbol('[[');
	    $interpolateProvider.endSymbol(']]');
    });

    mod.config(['growlProvider', function(growlProvider) {
        growlProvider.globalTimeToLive(5000);
    }]);

    mod.config(['$modalProvider', function($modalProvider) {
        $modalProvider.options.size = "lg";
    }]);


    // IE8 compatability mode!
    mod.config(function($sceProvider){
        $sceProvider.enabled(false);
    });

    mod.config(function($resourceProvider) {
        $resourceProvider.defaults.stripTrailingSlashes = false;
    });

    return mod;
};

OPAL.run = function(app){
    app.run([
        '$rootScope',
        'ngProgressLite',
        '$modal',
        '$location',
        '$analytics',
        '$window',
        OPAL._run
    ]);
};

OPAL._track = function($location, $analytics, $window){
    var track, not_qs, path;

    if(this.tracking.manualTrack){
        path = $window.location.pathname + $window.location.hash;

        track = _.some(this.tracking.opal_angular_exclude_tracking_prefix, function(prefix){
            return path.indexOf((prefix)) === 0;
        });

        if(!track){
            not_qs = _.some(this.tracking.opal_angular_exclude_tracking_qs, function(qs){
                return path === qs;
            });

            if(not_qs){
                $analytics.pageTrack($location.path());
            }
            else{
                $analytics.pageTrack($location.url());
            }
        }
    }
};

OPAL._run = function($rootScope, ngProgressLite, $modal, $location, $analytics, $window) {

    // Let's allow people to know what version they're running
    $rootScope.OPAL_VERSION = version;

    // When route started to change.
    $rootScope.$on('$routeChangeStart', function() {
        OPAL._track($location, $analytics, $window);
        ngProgressLite.set(0);
        ngProgressLite.start();
    });

    // When route successfully changed.
    $rootScope.$on('$routeChangeSuccess', function() {
        ngProgressLite.done();
    });

    // When some error occured.
    $rootScope.$on('$routeChangeError', function() {
        ngProgressLite.set(0);
    });

    $rootScope.dateHelper = {
      now: function(){ return new Date(); },
      yesterday: function(){
        return moment().subtract(1, 'days').toDate();
      }
    }

    $rootScope.open_modal = function(controller, template, resolves){
        $rootScope.state = 'modal';

        resolve = {};
        _.each(_.keys(resolves), function(key){
            resolve[key] = function(){
                return resolves[key];
            };
        });

        var reset = function(){
            $rootScope.state = 'normal';
        }

        return $modal.open({
            controller : controller,
            templateUrl: template,
            resolve    : resolve
        }).result.then(
            reset, reset
        );
    };
};

// From http://stackoverflow.com/a/3937924/2463201
jQuery.support.placeholder = (function(){
	var i = document.createElement('input');
	return 'placeholder' in i;
})();
