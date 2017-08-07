angular.module(
    'opal.services'
).factory(
    'Flow',
    function($q, $http, $modal, $cacheFactory, $injector){
        "use strict";
        var get_flow_service = function(){
            var OPAL_FLOW_SERVICE = $injector.get('OPAL_FLOW_SERVICE');
            if(OPAL_FLOW_SERVICE){
                return $injector.get(OPAL_FLOW_SERVICE);
            }else{
                return {
                    enter:  function(){
                        return {
                            'controller': 'HospitalNumberCtrl',
                            'template'  : '/templates/modals/hospital_number.html/'
                        };
                    },
                    exit: function(){
                        return  {
                            'controller': 'DischargeEpisodeCtrl',
                            'template'  : '/templates/modals/discharge_episode.html/'
                        };
                    }
                };
            }
        }


        var Flow = {

            enter: function(config, context){
                var deferred = $q.defer();
                var target = get_flow_service().enter();
                var result = $modal.open({
                    backdrop: 'static',
                    templateUrl: target.template,
                    controller:  target.controller,
                    resolve: {
                        referencedata:   function(Referencedata){ return Referencedata.load() },
                        metadata:        function(Metadata){ return Metadata.load(); },
                        tags:            function(){ return config.current_tags},
                        hospital_number: function(){ return config.hospital_number; },
                        context:         function(){ return context; }
                    }
                }).result;
                deferred.resolve(result);
                return deferred.promise;
            },

            exit: function(episode, config, context){
                var deferred = $q.defer();
                var target = get_flow_service().exit(episode)
                var result = $modal.open({
                    backdrop: 'static',
                    templateUrl: target.template,
                    controller:  target.controller,
                    keyboard: false,
                    resolve: {
                        episode      : function() { return episode; },
                        referencedata: function(Referencedata){ return Referencedata.load() },
                        metadata     : function(Metadata){ return Metadata.load(); },
                        tags         : function() { return config.current_tags; },
                        context      : function(){ return context; }
      			    }
                }).result;

                deferred.resolve(result);
                return deferred.promise;
            }

        };
        return Flow;
    }
);
