angular.module(
    'opal.services'
).factory(
    'Flow',
    function($q, $http, $modal, $cacheFactory){
        
        var flow_cache = $cacheFactory('flow-cache');

        // 
        // Return the correct flow object for the current
        // situation
        // 
        var flow_for_verb = function(verb, current_tags){
            var flow = flow_cache.get('flow');
            if(!current_tags){
                return flow['default'][verb];
            }
            if(current_tags.tag && current_tags.tag in flow){
                if(current_tags.subtag && current_tags.subtag in flow){
                    return flow[current_tags.tag][current_tags.subtag][verb];
                }else{
                    return flow[current_tags.tag]['default'][verb];
                }
            }else{// Default
                return flow['default'][verb];
            }
        }

        return function(verb, schema, options, config){
            var deferred = $q.defer();
            var datadeferred = $q.defer();

            if(flow_cache.get('flow')){
                datadeferred.resolve()
            }else{
                $http.get('/flow/').then(
                    // Success
                    function(response){
                        flow_cache.put('flow', response.data);
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
                        var flow = flow_for_verb('enter', config.current_tags);

		                result = $modal.open({
			                templateUrl: flow.template,
			                controller:  flow.controller,
                            resolve: {
                                schema:          function(){ return schema },
                                options:         function(){ return options },
                                tags:            function(){ return options.current_tags},
                                hospital_number: function(){ return options.hospital_number; }
                            }
		                }).result;
                        deferred.resolve(result);
                    })
                },

                // The patient is 'leaving'. Do the right thing.
                exit: function(schema, options, config){
                    datadeferred.promise.then(function(){
                        var flow = flow_for_verb('exit', config.current_tags);
                        
		                result = $modal.open({
			                templateUrl: flow.template,
			                controller:  flow.controller,
			                resolve: {
				                episode: function() { return config.episode; },
                                tags   : function() { return config.current_tags }
			                }
		                }).result
                        deferred.resolve(result);
                    });
                },
            }

            verbs[verb](schema, options, config)

            return deferred.promise
            
        }
    }
);
