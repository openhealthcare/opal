angular.module('opal.controllers').controller(
    'EpisodeRedirectListCtrl', function($scope, $cookieStore, $location, patientListLoader){
        "use strict";
        // a simple controller that redirects to the correct tag/subtag
        $scope.ready = false;
        var patientLists;
        var slug =  $cookieStore.get('opal.listSlug');
        var path_base = '/list/';
        slug = false;

        function redirectToSlug(slug){
          $location.path(path_base + slug);
          $location.replace();
        }

        if(slug){
          redirectToSlug(data[0])
        }
        else{
            var patientLists = patientListLoader();
            patientListLoader().then(function(data){
              redirectToSlug(data[0].slug)
            });
        }
});
