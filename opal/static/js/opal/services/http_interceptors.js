angular.module('opal.services').factory('LogoutInterceptor', function($q, $window){
  var logout = {
    responseError: function(rejection){
      if(rejection.status === 403 || rejection.status === 401){
        $window.location.pathname = '/accounts/logout/';
      }
      return $q.reject(rejection);
    }
  };

  return logout;
});

angular.module('opal.services').config(['$httpProvider', function($httpProvider) {
  $httpProvider.interceptors.push('LogoutInterceptor');
}]);
