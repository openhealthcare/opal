//
// Editing/detail page for ward round episodes
//
angular.module('opal.controllers').controller(
   'PatientDetailCtrl', function($rootScope, $scope, $cookieStore,
                                episodes, options, profile, recordLoader,
                                EpisodeDetailMixin
                                   ){

        microEpisodes = _.filter(episodes, function(e){
           return e.microbiology_input && e.microbiology_input.length;
       });
       $scope.episodes = _.sortBy(microEpisodes, function(e){
           var significantDate = e.date_of_discharge || e.date_of_episode || e.date_of_admission;
           if(significantDate){
               return significantDate.unix * -1;
           }
       });

       $scope.profile = profile;
       $scope.options = options;

       if($scope.episodes.length){
           $scope.episode = $scope.episodes[0];
           EpisodeDetailMixin($scope);
       }

       $scope.patient = episodes[0].demographics[0];
       $scope.lastInputId = _.last(_.last($scope.episodes).microbiology_input).id;

       $scope.getEpisodeLink = function(episode){
           return "/#/episode/" + episode.id
       }
   }
);
