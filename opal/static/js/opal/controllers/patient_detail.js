//
// Editing/detail page for ward round episodes
//
angular.module('opal.controllers').controller(
   'PatientDetailCtrl', function($rootScope, $scope, $cookieStore,
                                episodes, options, profile
                                   ){

       $scope.episodes = _.sortBy(episodes, function(e){
           var significantDate = e.date_of_discharge || e.date_of_episode || e.date_of_admission;
           if(significantDate){
               return significantDate.unix * -1;
           }
       });

       $scope.patient = $scope.episodes[0].demographics[0];
        //    $scope.episodeLink = _.partial(wardroundUtils.episodeLink, $routeParams.wardround);
       $scope.options = options;
       $scope.profile = profile;

       if($scope.episodes.length){
           $scope.lastInputId = _.last(_.last($scope.episodes).microbiology_input).id;
       }

       $scope.getEpisodeLink = function(episode){
           return "/#/episode/" + episode.id
       }
   }
);
