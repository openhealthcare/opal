angular.module('opal.controllers').controller(
    'PatientDetailCtrl',
    function(
        $rootScope, $scope, $modal, $location, $routeParams,
        Item, patientLoader, patient, profile, metadata
    ){
        $scope.profile = profile;
        $scope.patient = patient;
        if($scope.patient != null){
            $scope.episode = patient.episodes[0];
        }
        $scope.view = null;

        $scope.refresh = function(){
          patientLoader().then(function(refreshedPatient){
            $scope.patient = refreshedPatient;
            $scope.episode = _.findWhere($scope.patient.episodes, {id: $scope.episode.id});
          });
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
        }

        $scope.switch_to_episode = function(index, $event){
            if($event){
                $event.preventDefault()

            }
            $scope.episode = $scope.patient.episodes[index];
            $scope.view = null;
            return true
        }

        $scope.switch_to_view = function(what){
            $scope.view = what;
            return true
        }

      if($scope.patient != null){
            $scope.initialise();
        }
    }
);
