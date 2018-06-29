describe('LogoutInterceptor', function(){
  "use strict";

  var LogoutInterceptor, $q, httpProvider ;
  var $window = {location: {pathname: "somePath"}};

  beforeEach(function(){
    module('opal.services', function($httpProvider, $provide){
        httpProvider = $httpProvider;
        $provide.service('$window', function(){
          $window.location.pathname = "somePath";
          return $window;
        });

        $provide.service('')
    });
    inject(function($injector){
      $q = $injector.get('$q');
      LogoutInterceptor = $injector.get('LogoutInterceptor');
    });

    spyOn($q, "reject");
  });

  it('should redirect for 403s', function(){
    LogoutInterceptor.responseError({status: 403});
    expect($window.location.pathname).toBe("/accounts/logout/");
  });

  it('should redirect for 401s', function(){
    LogoutInterceptor.responseError({status: 401});
    expect($window.location.pathname).toBe("/accounts/logout/");
  });

  it('should not redirect for other status codes', function(){
    LogoutInterceptor.responseError({status: 500});
    expect($window.location.pathname).toBe("somePath");
    expect($q.reject).toHaveBeenCalledWith({status: 500});
  });

  it('should put the interceptor on to the http providers', function(){
    expect(httpProvider.interceptors).toEqual(['LogoutInterceptor']);
  });
});
