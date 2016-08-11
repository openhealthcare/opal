//
// Placeholder Flow service.
//
// To enable this service for custom flow:
//
// 1. Add it to your application javascripts
// 2. Set the name of the service as the setting OPAL_FLOW_SERVICE
// 3. Implement your custom logic.
//
angular.module('opal.services').factory('AppFlow', function($routeParams){

    var ApplicationFlow = {
        enter:  function(){
            return {
                'controller': 'HospitalNumberCtrl',
                'template'  : '/templates/modals/hospital_number.html/'
            }
        },
        exit: function(){
            return  {
                'controller': 'DischargeEpisodeCtrl',
                'template'  : '/templates/modals/discharge_episode.html/'
            }
        }
    };

    return ApplicationFlow;

});
