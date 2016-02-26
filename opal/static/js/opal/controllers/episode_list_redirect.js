angular.module('opal.controllers').controller(
    'EpisodeRedirectListCtrl', function($scope, $cookieStore, $location, options){
        "use strict";
        // a simple controller that redirects to the correct tag/subtag
        $scope.ready = false;

        var path_base = '/list/';
        var last_list = $cookieStore.get('opal.lastPatientList');
        if(last_list){
            var target = path_base + last_list;
        }else{
            var target = _.keys(options.tag_hierarchy)[0];
            if(options.tag_hierarchy[target].length > 0){
                target += '-' + options.tag_hierarchy[target][0];
            }
            target = path_base + target;
        }
        $location.path( target + '/');
        $location.replace();
});
