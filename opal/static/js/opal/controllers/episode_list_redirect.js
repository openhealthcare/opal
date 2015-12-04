angular.module('opal.controllers').controller(
    'EpisodeRedirectListCtrl', function($scope, $cookieStore, $location, options){
        "use strict";
        // a simple controller that redirects to the correct tag/subtag
        $scope.ready = false;
        var tag =  $cookieStore.get('opal.currentTag') || _.keys(options.tag_hierarchy)[0];
        var subtag =  $cookieStore.get('opal.currentSubTag') || "";
        var path_base = '/list/';

        if(!subtag){
            if(tag in options.tag_hierarchy &&
                options.tag_hierarchy[tag].length > 0){
                subtag = options.tag_hierarchy[tag][0];
            }
        }
        $location.path(path_base + tag + "/" + subtag);
});
