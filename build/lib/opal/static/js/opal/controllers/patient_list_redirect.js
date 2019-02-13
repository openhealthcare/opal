angular.module('opal.controllers').controller(
    'PatientListRedirectCtrl', function($scope, $cookies, $location, metadata){
        "use strict";
        var target;
        $scope.ready = false;

        var replacePath = function(last_list){
            var path_base = '/list/';
            target = path_base + last_list;
            $location.path(target + '/');
            $location.replace();
        };

        var last_list = $cookies.get('opal.previousPatientList');
        if(last_list){
            replacePath(last_list);
        }else{
            replacePath(metadata.first_list_slug);
        }
    });
