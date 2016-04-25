angular.module('opal.controllers').controller(
    'PatientListRedirectCtrl', function($scope, $cookieStore, $location, options){
        "use strict";
        // a simple controller that redirects to the correct tag/subtag
        var target;
        $scope.ready = false;

        var path_base = '/list/';
        var last_list = $cookieStore.get('opal.lastPatientList');
        if(last_list){
            target = path_base + last_list;
        }else{
            target = path_base + options.first_list_slug;
        }
        $location.path(target + '/');
        $location.replace();
});
