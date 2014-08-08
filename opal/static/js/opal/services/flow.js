angular.module(
    'opal.services'
).factory(
    'Flow',
    function($q, $http, $modal, $cacheFactory){
        
        var flowCache = $cacheFactory('flow-cache');
        var GOT_FLOW = false;

        return function(verb, schema, options, config){
            var deferred = $q.defer();
            var datadeferred = $q.defer();

            if(flowCache.get('flow')){
                datadeferred.resolve()
            }else{
                $http.get('/flow/').then(
                    // Success
                    function(response){
                        flowCache.put('flow', response.data);
                        datadeferred.resolve()
                    },
                    // Error
                    function(response){
                        alert('An error occurred - please inform someone!');
                    }
                )
            }            

            var verbs = {            
                // The patient is 'entering'. Do the right thing.
                enter: function(schema, options, config){

                    datadeferred.promise.then(function(){
                        var flow = flowCache.get('flow');

                        var templateUrl = flow['default'].enter.template;
                        var controller = flow['default'].enter.controller;

		                result = $modal.open({
			                templateUrl: templateUrl,
			                controller: controller,
                            resolve: {
                                schema: function(){ return schema },
                                options: function(){ return options },
                                tags: function(){ return options.current_tags},
                                hospital_number: function(){ return null; }
                            }
		                }).result;

                        deferred.resolve(result);
                    })
                },

                // The patient is 'leaving'. Do the right thing.
                exit: function(schema, options, config){
                    
                },
            }

            verbs[verb](schema, options, config)

            return deferred.promise
            
        }
    }
);
