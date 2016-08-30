var OPAL = {};
if(undefined === version){
    var version = 'test';
}
if(undefined === OPAL_FLOW_SERVICE){
    var OPAL_FLOW_SERVICE = null;
}

OPAL._configure = function(mod){
  // See http://stackoverflow.com/questions/8302928/angularjs-with-django-conflicting-template-tags
  mod.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
  });

  mod.config(['growlProvider', function(growlProvider) {
      growlProvider.globalTimeToLive(5000);
  }]);


  // IE8 compatability mode!
  mod.config(function($sceProvider){
      $sceProvider.enabled(false);
  });

  mod.config(function($resourceProvider) {
      $resourceProvider.defaults.stripTrailingSlashes = false;
  });

  mod.config(function(IdleProvider) {
    // show log out modal after 10 mins
    IdleProvider.idle(settings.OPAL_LOG_OUT_DURATION || 600);
    var opalTimeout = 900;
    IdleProvider.timeout(opalTimeout);
  });

  if(OPAL._trackingConfig.manualTrack){
    mod.config(function($analyticsProvider) {
        $analyticsProvider.virtualPageviews(false);
    });
  }

  return mod;
}

OPAL.module = function(namespace, dependencies){
    dependencies = dependencies || [];

    if(OPAL_ANGULAR_DEPS === undefined){
        var OPAL_ANGULAR_DEPS = [];
    }

    var implicit_dependencies = [
        'angular-growl',
        'mentio',
        'angulartics',
        'angulartics.google.analytics',
        'LocalStorageModule',
        'ngIdle'
    ];

    _.each(implicit_dependencies, function(dependency){
        if(!_.contains(dependencies, dependency)){
            dependencies.push(dependency);
        }
    });


    OPAL._trackingConfig = {
      manualTrack: window.OPAL_ANGULAR_EXCLUDE_TRACKING_PREFIX || window.OPAL_ANGULAR_EXCLUDE_TRACKING_QS,
      opal_angular_exclude_tracking_prefix: window.OPAL_ANGULAR_EXCLUDE_TRACKING_PREFIX || [],
      opal_angular_exclude_tracking_qs: window.OPAL_ANGULAR_EXCLUDE_TRACKING_QS || []
    };

    _.each(OPAL_ANGULAR_DEPS, function(d){
        dependencies.push(d);
    });

    var mod = angular.module(namespace, dependencies);

    return OPAL._configure(mod);
};

OPAL.run = function(app){
    app.run([
        '$rootScope',
        'ngProgressLite',
        '$modal',
        '$window',
        '$location',
        '$analytics',
        'Idle',
        OPAL._run
    ]);
};

OPAL._track = function($location, $analytics){
    var track, not_qs, path;

    if(OPAL._trackingConfig.manualTrack){
        path = $location.path();

        track = _.some(OPAL._trackingConfig.opal_angular_exclude_tracking_prefix, function(prefix){

            return path.indexOf((prefix)) === 0;
        });

        if(!track){
            not_qs = _.some(OPAL._trackingConfig.opal_angular_exclude_tracking_qs, function(qs){
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

OPAL._run = function($rootScope, ngProgressLite, $modal, $window, $location, $analytics, Idle) {
    if(Idle){
      Idle.watch();
    }

    // Let's allow people to know what version they're running
    $rootScope.OPAL_VERSION = version;

    // When route started to change.
    $rootScope.$on('$routeChangeStart', function() {
        OPAL._track($location, $analytics);
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

    $rootScope.open_modal = function(controller, template, size, resolves){
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
            size       : size,
            resolve    : resolve
        }).result.then(
            reset, reset
        );
    };

    $rootScope.$on('IdleStart', function() {
      $rootScope.open_modal(
        'KeyBoardShortcutsCtrl',
        '/templates/logout_modal.html',
        'lg'
      );
     });

    $rootScope.$on('IdleTimeout', function() {
      $window.location.pathname = '/accounts/logout/';
    });
};


// From http://stackoverflow.com/questions/3629183/why-doesnt-indexof-work-on-an-array-ie8
_indexof = function(elt /*, from*/)
	{
		var len = this.length >>> 0;
		var from = Number(arguments[1]) || 0;
		from = (from < 0)
		    ? Math.ceil(from)
		    : Math.floor(from);
		if (from < 0)
			from += len;

		for (; from < len; from++)
		{
			if (from in this &&
			    this[from] === elt)
				return from;
		}
		return -1;
	};
if (!Array.prototype.indexOf) {
	Array.prototype.indexOf = _indexof
}


// From http://stackoverflow.com/a/3937924/2463201
jQuery.support.placeholder = (function(){
	var i = document.createElement('input');
	return 'placeholder' in i;
})();


// Fuck you Internet Explorer 8
if (typeof String.prototype.trim !== 'function') {
	String.prototype.trim = function() {
		return this.replace(/^\s+|\s+$/g, '');
	}
}


// // From http://stackoverflow.com/a/2897510/2463201
// jQuery.fn.getCursorPosition = function() {
//     var self = this;
// 	var input = self.get(0);
// 	if (!input) return; // No (input) element found
// 	if ('selectionStart' in input) {
// 		// Standard-compliant browsers
// 		return input.selectionStart;
// 	} else if (document.selection) {
// 		// IE
// 		input.focus();
// 		var sel = document.selection.createRange();
// 		var selLen = document.selection.createRange().text.length;
// 		sel.moveStart('character', -input.value.length);
// 		return sel.text.length - selLen;
// 	}
// }
