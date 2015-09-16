describe('DeleteItemConfirmationCtrl', function(){
    var $scope, $timeout;
    var item, $modalInstance;

    beforeEach(function(){
        module('opal', function($provide) {
            $provide.value('$analytics', function(){
                return {
                    pageTrack: function(x){}
                }
            });

            $provide.provider('$analytics', function(){
                this.$get = function() {
                    return {
                        virtualPageviews: function(x){},
                        settings: {
                            pageTracking: false,
                        },
                        pageTrack: function(x){}
                     };
                };
            });
        });
    });

    beforeEach(function(){
        inject(function($injector){
            $rootScope  = $injector.get('$rootScope');
            $scope      = $rootScope.$new();
            $controller = $injector.get('$controller');
            $timeout    = $injector.get('$timeout');
            $modal      = $injector.get('$modal');
            $q          = $injector.get('$q')
        });

        $modalInstance = $modal.open({template: 'notarealtemplate'});
        item = { destroy: function(){} };

        controller = $controller('DeleteItemConfirmationCtrl', {
            $scope        : $scope,
            $timeout      : $timeout,
            $modalInstance: $modalInstance,
            item          : item
        });
    });

    describe('deleting', function(){
        it('should call destroy on the modal', function(){
            var deferred;

            deferred = $q.defer();
            spyOn(item, 'destroy').and.returnValue(deferred.promise);
            spyOn($modalInstance, 'close');

            $scope.destroy();
            deferred.resolve();
            $rootScope.$apply();

            expect(item.destroy).toHaveBeenCalledWith();
            expect($modalInstance.close).toHaveBeenCalledWith('deleted');
        })
    });

    describe('cancelling', function(){
        it('should close the modal', function(){
            spyOn($modalInstance, 'close');
            $scope.cancel();
            expect($modalInstance.close).toHaveBeenCalledWith('cancel')
        })
    });
});
