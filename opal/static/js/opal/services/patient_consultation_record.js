angular.module('opal.services').service('PatientConsultationRecord', function($window){
    return function(item){
      if(!item.initial){
        item.initials = $window.initials;
      }

      if(!item.when){
        item.when = moment();
      }
    };
});
