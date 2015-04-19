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
                if(current_tags.subtag && current_tags.subtag in flow[current_tags.tag]){
                    if(verb in flow[current_tags.tag][current_tags.subtag]){
                        return flow[current_tags.tag][current_tags.subtag][verb];
                    }           // TODO: ELSE
                }else{
                    if(flow[current_tags.tag]['default'] && 
                       flow[current_tags.tag]['default'][verb]){
                        // The tag has this verb in it's default
                        return flow[current_tags.tag]['default'][verb];
                    }else {
                        return flow['default'][verb];
                    }
                    
                }
            }else{// Default
                return flow['default'][verb];
            }
        };

        var Flow = function(verb, schema, options, config){
            var deferred = $q.defer();
            var datadeferred = $q.defer();

            if(flow_cache.get('flow')){
                datadeferred.resolve()
            }else{
                $http.get('/api/v0.1/flow/').then(
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
                //
                // Config params:
                //   hospital_number - the hospital number we're entering for
                //   current_tags - a tags object representing a current list
                //
                enter: function(schema, options, config){
                    datadeferred.promise.then(function(){
                        var flow = flow_for_verb('enter', config.current_tags);

		                result = $modal.open({
			                templateUrl: flow.template,
			                controller:  flow.controller,
                            resolve: {
                                schema:          function(){ return schema },
                                options:         function(){ return options },
                                tags:            function(){ return config.current_tags},
                                hospital_number: function(){ return config.hospital_number; }
                            }
		                }).result;
                        deferred.resolve(result);
                    })
                },

                // The patient is 'leaving'. Do the right thing.
                //
                // Config params:
                //   episode - the episode that is exiting
                //   current_tags - a tags object representing a current list
                //
                exit: function(schema, options, config){
                    datadeferred.promise.then(function(){
                        var flow = flow_for_verb('exit', config.current_tags);
                        
		                result = $modal.open({
			                templateUrl: flow.template,
			                controller:  flow.controller,
                            keyboard: false,
			                resolve: {
				                episode: function() { return config.episode; },
                                tags   : function() { return config.current_tags; },
                                options: function() { return options; },
                                schema : function() { return schema; }
			                }
		                }).result
                        deferred.resolve(result);
                    });
                },
            }

            verbs[verb](schema, options, config)

            return deferred.promise
            
        }
        
        Flow.flow_for_verb = flow_for_verb;
        return Flow;
    }
);
