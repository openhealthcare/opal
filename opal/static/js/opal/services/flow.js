angular.module(
    'opal.services'
).factory(
    'Flow',
    function($q, $http, $modal, $cacheFactory, $injector){
        var ApplicationFlow;

        if(OPAL_FLOW_SERVICE){
            ApplicationFlow = $injector.get(OPAL_FLOW_SERVICE);
        }else{
            ApplicationFlow = {
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

        var Flow = {

            enter: function(config, context){
                var deferred = $q.defer();
                var target = ApplicationFlow.enter();
                result = $modal.open({
                    backdrop: 'static',
                    templateUrl: target.template,
                    controller:  target.controller,
                    resolve: {
                        referencedata:   function(Referencedata){ return Referencedata; },
                        metadata:        function(Metadata){ return Metadata; },
                        tags:            function(){ return config.current_tags; },
                        hospital_number: function(){ return config.hospital_number; },
                        context:         function(){ return context; }
                    }
                }).result;
                deferred.resolve(result);
                return deferred.promise;
            },

            exit: function(episode, config, context){
                var deferred = $q.defer();
                var target = ApplicationFlow.exit(episode);
                result = $modal.open({
                    backdrop: 'static',
                    templateUrl: target.template,
                    controller:  target.controller,
                    keyboard: false,
                    resolve: {
                        episode      : function() { return episode; },
                        referencedata: function(Referencedata){ return Referencedata; },
                        metadata     : function(Metadata){ return Metadata; },
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
