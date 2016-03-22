angular.module(
    'opal.services'
).factory(
    'Flow',
    function($q, $http, $modal, $cacheFactory, $injector){
        var ApplicationFlow = $injector.get('elCIDFlow');
        var Flow = {

            enter: function(options, config){
                var deferred = $q.defer();
                var target = ApplicationFlow.enter();

		        result = $modal.open({
                    size: 'lg',
                    backdrop: 'static',
			        templateUrl: target.template,
			        controller:  target.controller,
                    resolve: {
                        options:         function(){ return options },
                        tags:            function(){ return config.current_tags},
                        hospital_number: function(){ return config.hospital_number; }
                    }
		        }).result;
                deferred.resolve(result);
                return deferred.promise;
            },

            exit: function(episode, options, config){
                var deferred = $q.defer();
                var target = ApplicationFlow.exit(episode)
		        result = $modal.open({
                    size: 'lg',
                    backdrop: 'static',
			        templateUrl: target.template,
			        controller:  target.controller,
                    keyboard: false,
			        resolve: {
				        episode: function() { return episode; },
                        tags   : function() { return config.current_tags; },
                        options: function() { return options; },
			        }
		        }).result
                deferred.resolve(result);
                return deferred.promise
            }

        }
        return Flow;
    }
);
