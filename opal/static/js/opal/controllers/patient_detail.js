angular.module('opal.controllers').controller(
    'PatientDetailCtrl',
    function(
        $scope, $routeParams, patientLoader, patient, profile, metadata, $q, $location, $window
    ){
        $scope.profile = profile;
        $scope.patient = patient;
        var routeUrl = "/patient/" + $routeParams.patient_id + "/"
        if($scope.patient != null){
            $scope.episode = patient.episodes[0];
        }
        $scope.view = null;

        $scope.refresh = function(){
          var deferred = $q.defer();
          patientLoader().then(function(refreshedPatient){
            $scope.patient = refreshedPatient;
            $scope.episode = _.findWhere($scope.patient.episodes, {id: $scope.episode.id});
            deferred.resolve();
          });
          return deferred.promise;
        };

        $scope.initialise = function(){
            $scope.metadata = metadata;

            if($routeParams.view){
                if(_.isNaN(parseInt($routeParams.view))){
                    $scope.switch_to_view($routeParams.view);
                }else{
                    var index = null
                    var target = parseInt($routeParams.view);
                    _.each($scope.patient.episodes, function(episode, i){
                        if(episode.id == target){
                            index = i;
                        }
                    });
                    if(index != null){
                        $scope.switch_to_episode(index);
                    }
                }
            }
            $scope.metadata = metadata;
        };

        $scope.switch_to_episode = function(index, $event){
            if($event){
                $event.preventDefault()
            }
            $scope.episode = $scope.patient.episodes[index];
            $scope.view = null;
            var newUrl = routeUrl + $scope.episode.id;
            if(newUrl !== $location.url()){
                $location.url(routeUrl + $scope.episode.id);
                $("html, body").scrollTop(0);;
                $location.replace();
                $window.history.pushState(null, 'any', $location.absUrl());
            }
            return true
        }

        $scope.switch_to_view = function(what){
            $scope.view = what;
            var newUrl = routeUrl + what;
            if(newUrl !== $location.url()){
                $location.url(routeUrl + what);
                $("html, body").scrollTop(0);;
                $location.replace();
                $window.history.pushState(null, 'any', $location.absUrl());
            }
            return true
        }

      if($scope.patient != null){
           $scope.initialise();
        }
    }
);
