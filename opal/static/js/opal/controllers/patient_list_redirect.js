angular.module('opal.controllers').controller(
  'PatientListRedirectCtrl', function($scope, $cookieStore, $location, options){
  "use strict";
  var target;
  $scope.ready = false;

  var replacePath = function(last_list){
    var path_base = '/list/';
    target = path_base + last_list;
    $location.path(target + '/');
    $location.replace();
  };

  var last_list = $cookieStore.get('opal.lastPatientList');
  if(last_list){
    replacePath(last_list);
  }else{
    replacePath(options.first_list_slug);
    // Options.then(function(options){
    //   replacePath(options.first_list_slug);
    // });
  }
});

// angular.module('opal.controllers').controller(
//     'PatientListRedirectCtrl', function($scope, $cookieStore, $location, options){
//         "use strict";
//         // a simple controller that redirects to the correct tag/subtag
//         $scope.ready = false;
//
//         var path_base = '/list/';
//         var last_list = $cookieStore.get('opal.lastPatientList');
//         if(last_list){
//             var target = path_base + last_list;
//         }else{
//             var target = path_base + options.first_list_slug;
//         }
//         $location.path( target + '/');
//         $location.replace();
// });
