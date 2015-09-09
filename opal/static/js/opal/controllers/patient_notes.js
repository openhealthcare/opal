//
// Editing/detail page for ward round episodes
//
angular.module('opal.controllers').controller(
   'PatientDetailCtrl', function($rootScope, $scope, $cookieStore,
                                episodes, options, profile, recordLoader,
                                EpisodeDetailMixin, ngProgressLite, $q
                                   ){

        COOKIE_NAME = "patientNotes-inlineForm";

       $scope.episodes = _.sortBy(episodes, function(e){
           var significantDate = e.date_of_discharge || e.date_of_episode || e.date_of_admission;
           if(significantDate){
               return significantDate.unix * -1;
           }
       });

       $scope.inlineForm = {};

       $scope.initialiseForm = function(default_arg){
           $scope.inlineForm.name = $cookieStore.get(COOKIE_NAME) || default_arg;
       };

       $scope.$watch("inlineForm.name", function(){
           if($scope.inlineForm.name){
               $cookieStore.put(COOKIE_NAME, $scope.inlineForm.name);
           }
       }, true);

       $scope.profile = profile;
       $scope.options = options;

       function getResistantOrganisms(episode){
           if(episode.microbiology_test){
               return _.reduce(episode.microbiology_test, function(r, mt){
                   if(mt.resistant_antibiotics){
                       r.push(mt.resistant_antibiotics);
                   }

                   return r;
               }, []);
           }
       }

       if($scope.episodes.length){
           $scope.episode = $scope.episodes[0];

           $scope.episode.resistantOrganisms = function(){
                   return _.reduce(episodes, function(r, e){
                   var resistantOrganisms = getResistantOrganisms(e);
                   if(resistantOrganisms.length){
                       r = r.concat(resistantOrganisms);
                   }

                   return r;
               }, []);
           };

           EpisodeDetailMixin($scope);
           $scope.lastInputId = _.last(_.last($scope.episodes).microbiology_input).id;
       }

       $scope.patient = episodes[0].demographics[0];

       $scope.getEpisodeLink = function(episode){
           return "/#/episode/" + episode.id;
       };
   }
);
