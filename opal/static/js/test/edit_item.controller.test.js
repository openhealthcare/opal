describe('EditItemCtrl', function (){
    "use strict";

    var $scope, $timeout, $modal, $httpBackend;
    var item, Item, opalTestHelper;
    var Episode, episode, ngProgressLite, $q, $rootScope;
    var $controller, controller, fakeModalInstance;
    var $analytics, metadataCopy, profile, referencedata;

    beforeEach(function(){
      module('opal.controllers');
      module('opal.test');
    });

    beforeEach(function(){
        $analytics = jasmine.createSpyObj(["eventTrack"]);

        inject(function($injector){
            Item           = $injector.get('Item');
            Episode        = $injector.get('Episode');
            $controller    = $injector.get('$controller');
            $q             = $injector.get('$q');
            $httpBackend   = $injector.get('$httpBackend');
            $timeout       = $injector.get('$timeout');
            $modal         = $injector.get('$modal');
            ngProgressLite = $injector.get('ngProgressLite');
            $rootScope     = $injector.get('$rootScope');
            $modal         = $injector.get('$modal');
            opalTestHelper = $injector.get('opalTestHelper');
        });

        episode       = opalTestHelper.newEpisode($rootScope);
        metadataCopy  = opalTestHelper.getMetaData();
        profile       = opalTestHelper.getUserProfile();
        referencedata = opalTestHelper.getReferenceData();
        $scope        = $rootScope.$new();
        item          = new Item(
            {columnName: 'diagnosis'},
            episode,
            $rootScope.fields.diagnosis
        );

        fakeModalInstance = {
            close: function(){
                // do nothing
            },
        };

        controller = $controller('EditItemCtrl', {
            $scope        : $scope,
            $timeout      : $timeout,
            $modalInstance: fakeModalInstance,
            item          : item,
            metadata      : metadataCopy,
            profile       : profile,
            episode       : episode,
            ngProgressLite: ngProgressLite,
            referencedata : referencedata,
            $analytics    : $analytics
        });

    });

    describe('scope setup', function(){
      it('Should hoist metadata onto the scope', function () {
          expect($scope.metadata).toBe(metadataCopy);
      });

      it('Should set episode_category from episode.category_name', function() {
          expect($scope.episode_category).toBe("Inpatient");
      })

    })

    describe('editingMode()', function() {

        it('should know if this is edit or add', function() {
            expect($scope.editingMode()).toBe(false);
        });

    });

    describe('Saving items', function (){

        it('should save the episode if we have changed it', function() {
            $scope.$digest();
            var callArgs;
            var deferred = $q.defer();
            spyOn(item, 'save');
            spyOn(episode, 'save').and.callFake(function() {
                return deferred.promise;
            });
            $scope.episode.start = new Date();
            $scope.save('save');
            deferred.resolve("episode returned");
            $scope.$digest();

            callArgs = episode.save.calls.mostRecent().args;
            expect(callArgs.length).toBe(1);
            expect(callArgs[0]).toBe($scope.episode);
        });

        it('should cancel the progressbar if we fail to save', function() {
            var deferred = $q.defer();
            spyOn(ngProgressLite, 'done');
            spyOn(item, 'save').and.callFake(function() {
                return deferred.promise;
            });
            $scope.save('save');
            deferred.reject("Failure !!!");
            $scope.$digest();
            expect(ngProgressLite.done).toHaveBeenCalledWith();
        });

    });

    describe('delete()', function() {

        it('should open the delete modal', function() {
            spyOn($modal, 'open');
            $modal.open.and.returnValue({
                result: {
                    then: function(x){
                        x("cancelled");
                    }
                }
            });
            $scope.delete();
            expect($modal.open).toHaveBeenCalled()
            var args = $modal.open.calls.mostRecent().args[0];
            expect(args.templateUrl).toEqual('/templates/delete_item_confirmation_modal.html');
            expect(args.controller).toEqual('DeleteItemConfirmationCtrl');
            expect(args.resolve.item()).toEqual(item)
        });

        it('should return the output of the delete modal', function(){
            spyOn($modal, 'open');
            var promiseResolved = false;
            $modal.open.and.returnValue({
                result: {
                    then: function(x){
                        x("cancelled");
                    }
                }
            });
            spyOn($q, "defer").and.returnValue({
                resolve: function(result){
                    promiseResolved = result;
                }
            });

            $scope.delete("delete");
            expect(promiseResolved).toBe("cancelled");
        });
    });

    describe('cancel()', function(){

        it('should close with null', function(){
            spyOn(fakeModalInstance, 'close');
            $scope.cancel();
            expect(fakeModalInstance.close).toHaveBeenCalledWith('cancel');
        });

    });

});
