angular.module('opal.services').service('PatientConsultationRecord', function($window){
    return function(item){
      if(!item.initials){
        item.initials = $window.initials;
      }

      if(!item.when){
        item.when = moment();
      }
    };
});
