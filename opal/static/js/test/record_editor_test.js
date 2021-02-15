describe('RecordEditor', function(){
    "use strict";

    var $scope, $modal, $routeParams;
    var $rootScope, $q;
    var episode;
    var UserProfile;
    var opalTestHelper;
    var profile, $log;

    var columns = {
        "default": [
            {
                name: 'demographics',
                single: true,
                fields: [
                    {name: 'name', type: 'string'},
                    {name: 'date_of_birth', type: 'date'},
                ]},
            {
                name: 'location',
                single: true,
                fields: [
                    {name: 'category', type: 'string'},
                    {name: 'hospital', type: 'string'},
                    {name: 'ward', type: 'string'},
                    {name: 'bed', type: 'string'},
                    {name: 'date_of_admission', type: 'date'},
                    {name: 'tags', type: 'list'},
                ]},
            {
                name: 'diagnosis',
                single: false,
                fields: [
                    {name: 'condition', type: 'string'},
                    {name: 'provisional', type: 'boolean'},
                ]
            },
            {
                name: 'something',
                single: false,
                fields: [
                    {name: 'condition', type: 'string'},
                    {name: 'provisional', type: 'boolean'},
                ]
            }
        ]
    };
    var fields = {}
    _.each(columns.default, function(c){
        fields[c.name] = c;
    });

    beforeEach(function(){
        module('opal.services');
        module('opal.test');

        inject(function($injector){
            $rootScope = $injector.get('$rootScope');
            $scope = $rootScope.$new();
            $routeParams = $injector.get('$routeParams');
            $modal = $injector.get('$modal');
            $q = $injector.get('$q');
            UserProfile = $injector.get('UserProfile');
            opalTestHelper = $injector.get('opalTestHelper');
            $log = $injector.get('$log');
        });

        profile = opalTestHelper.getUserProfile();

        spyOn(UserProfile, "load").and.callFake(function(fn){
          return {
            then: function(fn){ return fn(profile);}
          };
        });

        spyOn($log, "warn");

        episode = opalTestHelper.newEpisode($rootScope);
    });

    describe("edit item", function(){
          it('should accept a url that is passed through to the modal open', function(){
            var deferred, callArgs;
            deferred = $q.defer();
            deferred.resolve();
            var modalPromise = deferred.promise;
            spyOn($modal, 'open').and.returnValue({result: modalPromise}  );
            episode.recordEditor.editItem('diagnosis', episode.diagnosis[0], '/custom_template/');
            $scope.$digest();
            callArgs = $modal.open.calls.mostRecent().args;
            expect(callArgs[0].templateUrl).toBe("/custom_template/")
          });

          it('should open the EditItemCtrl with an item', function(){
            var deferred, callArgs;
            deferred = $q.defer();
            deferred.resolve();
            var modalPromise = deferred.promise;
            var fakeMetadaa = {
              load: function(){ return "some metadata"; }
            };

            var fakeReferencedata = {
              load: function(){ return "some reference data"; }
            };

            spyOn($modal, 'open').and.returnValue({result: modalPromise}  );
            episode.recordEditor.editItem('diagnosis', episode.diagnosis[0]);
            $scope.$digest();
            callArgs = $modal.open.calls.mostRecent().args;
            expect(callArgs.length).toBe(1);
            expect(callArgs[0].controller).toBe('EditItemCtrl');
            expect(callArgs[0].templateUrl).toBe('/templates/modals/diagnosis.html/');
            var resolves = callArgs[0].resolve;
            expect(resolves.item()).toEqual(episode.diagnosis[0]);
            expect(resolves.episode()).toEqual(episode);
            expect(resolves.metadata(fakeMetadaa)).toEqual("some metadata");
            expect(resolves.referencedata(fakeReferencedata)).toEqual( "some reference data");
        });

          it('should pull modal size through from the schema if it exists', function() {
              var deferred, callArgs;
              deferred = $q.defer();
              deferred.resolve();
              var modalPromise = deferred.promise;

              spyOn($modal, 'open').and.returnValue({result: modalPromise}  );
              episode.recordEditor.editItem('demographics', episode.demographics[0]);
              $scope.$digest();
              callArgs = $modal.open.calls.mostRecent().args;
          });

          it('should open the use route slug appropriately', function(){
              var deferred, callArgs;
              deferred = $q.defer();
              deferred.resolve();
              var modalPromise = deferred.promise;

              spyOn($modal, 'open').and.returnValue({result: modalPromise}  );
              $routeParams.slug = 'tropical-all'
              episode.recordEditor.editItem('diagnosis', episode.diagnosis[0]);
              $scope.$digest();
              callArgs = $modal.open.calls.mostRecent().args;
              expect(callArgs.length).toBe(1);
              expect(callArgs[0].controller).toBe('EditItemCtrl');
              expect(callArgs[0].templateUrl).toBe('/templates/modals/diagnosis.html/tropical-all');
          });

          describe('for a readonly user', function(){
              beforeEach(function(){
                  profile.readonly = true;
              });

              it('should return null', function(){
                var deferred, callArgs;
                deferred = $q.defer();
                deferred.resolve();
                var modalPromise = deferred.promise;

                spyOn($modal, 'open').and.returnValue({result: modalPromise}  );
                episode.recordEditor.editItem('demographics', episode.demographics[0]);
                $scope.$digest();
                expect($modal.open.calls.count()).toBe(0);
              });

              afterEach(function(){
                  profile.readonly = false;
              });
          });

          it('should change state to "normal" when the modal is closed', function() {
              var deferred;

              deferred = $q.defer();
              spyOn($modal, 'open').and.returnValue({result: deferred.promise});

              episode.recordEditor.editItem('demographics', episode.demographics[0]);

              deferred.resolve('save');
              $rootScope.$apply();

              expect($rootScope.state).toBe('normal');
          });

          it("should handle the result of it is not a promise", function(){
            var deferred;
            var called = false

            deferred = $q.defer();
            spyOn($modal, 'open').and.returnValue({result: deferred.promise});
            episode.recordEditor.editItem('demographics', episode.demographics[0]).then(function(modalResult){
                called = modalResult == "save";
            });

            deferred.resolve('save');
            $rootScope.$apply();

            expect($rootScope.state).toBe('normal');
            expect(called).toBe(true);
          });

          it("should handle the result if it is a promise", function(){
            var deferred, nestedDeferred;
            var called = false

            deferred = $q.defer();
            nestedDeferred = $q.defer()

            spyOn($modal, 'open').and.returnValue({result: deferred.promise});
            episode.recordEditor.editItem('demographics', episode.demographics[0]).then(function(modalResult){
                called = modalResult == "delete";
            });

            nestedDeferred.resolve("delete")
            deferred.resolve(nestedDeferred.promise);
            $rootScope.$apply();

            expect($rootScope.state).toBe('normal');
            expect(called).toBe(true);
          });
    });

    describe("get item", function(){
      it("should handle the case where there are no episodes at this index of this type on the episode", function(){
        var result = episode.recordEditor.getItem("diagnosis", 2);
        expect(result).not.toBe(undefined);
      });

      it("should not create if it can find the expected value", function(){
        var result = episode.recordEditor.getItem("diagnosis", 1);
        // get's Dengue because its ordered by -date_of_diagnosis
        expect(result.condition).toBe('Dengue');
      });
    })

    describe("new item", function(){
      it('should create a new item', function(){
         var deferred, callArgs;
         deferred = $q.defer();
         spyOn($modal, 'open').and.returnValue({result: deferred.promise});
         episode.recordEditor.newItem('diagnosis');
         $scope.$digest();
         callArgs = $modal.open.calls.mostRecent().args;
         expect(callArgs.length).toBe(1);
         expect(callArgs[0].controller).toBe('EditItemCtrl');
         expect(callArgs[0].templateUrl).toBe('/templates/modals/diagnosis.html/');
      });

      it('should not create a new singletons', function(){
        var deferred, callArgs;
        deferred = $q.defer();
        spyOn($modal, 'open').and.returnValue({result: deferred.promise});
        episode.recordEditor.newItem('demographics');
        $scope.$digest();
        expect($modal.open.calls.count()).toBe(0);
      });

      it('should respond to $routeParams.slug', function(){
          var deferred, callArgs;
          deferred = $q.defer();
          spyOn($modal, 'open').and.returnValue({result: deferred.promise});
          $routeParams.slug = 'tropical-all';
          episode.recordEditor.newItem('diagnosis');
          $scope.$digest();
          callArgs = $modal.open.calls.mostRecent().args;
          expect(callArgs.length).toBe(1);
          expect(callArgs[0].controller).toBe('EditItemCtrl');
          expect(callArgs[0].templateUrl).toBe('/templates/modals/diagnosis.html/tropical-all');
      });
    });
});
