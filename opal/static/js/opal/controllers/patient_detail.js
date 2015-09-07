//
// Editing/detail page for ward round episodes
//
angular.module('opal.controllers').controller(
   'PatientDetailCtrl', function($rootScope, $scope, $cookieStore,
                                episodes, options, profile, recordLoader,
                                EpisodeDetailMixin, ngProgressLite, $q
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

       function cleanForm(){

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

           // TODO we probably don't want to use $scope.espisodes, we probably want episodes[0]
           recordLoader.then(function(){
               var item = $scope.episode.newItem(name, {column: $rootScope.fields.microbiology_input});
               defaults ={
                   created: new moment(),
                   initials: window.initals,
                   reason_for_interaction: "Microbiology meeting"
               }
               $scope.editing = item.makeCopy();
               angular.extend($scope.editing, defaults);
               $scope.save = function(){
                       ngProgressLite.set(0);
                       ngProgressLite.start();
                       to_save = [item.save($scope.editing)];
                       $q.all(to_save).then(function() {
                           ngProgressLite.done();
                           item = $scope.episode.newItem('microbiology_test', {column: $rootScope.fields.microbiology_input});
                           $scope.editing = item.makeCopy();
                           angular.extend($scope.editing, defaults);
           		    });
               };
           });
       }

       $scope.patient = episodes[0].demographics[0];

       $scope.getEpisodeLink = function(episode){
           return "/#/episode/" + episode.id;
       };
   }
);
