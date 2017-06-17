describe('RecordEditor', function(){
    "use strict";

    var $scope, $modal, $routeParams;
    var $rootScope, $q, $controller;
    var Flow, Episode, episode;
    var controller, UserProfile;
    var opalTestHelper;
    var profile;

    var episodeData = {
        id: 123,
        active: true,
        prev_episodes: [],
        next_episodes: [],
        demographics: [{
            id: 101,
            patient_id: 99,
            name: 'John Smith',
            date_of_birth: '1980-07-31'
        }],
        tagging: [{'mine': true, 'tropical': true}],
        location: [{
            category: 'Inepisode',
            hospital: 'UCH',
            ward: 'T10',
            bed: '15',
            date_of_admission: '2013-08-01',
        }],
        diagnosis: [{
            id: 102,
            condition: 'Dengue',
            provisional: true,
        }, {
            id: 103,
            condition: 'Malaria',
            provisional: false,
        }]
    };

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
            $controller = $injector.get('$controller');
            $modal = $injector.get('$modal');
            Episode = $injector.get('Episode');
            $q = $injector.get('$q');
            UserProfile = $injector.get('UserProfile');
            opalTestHelper = $injector.get('opalTestHelper');
        });

        profile = opalTestHelper.getUserProfile();

        spyOn(UserProfile, "load").and.callFake(function(fn){
          return {
            then: function(fn){ return fn(profile);}
          };
        });

        episode = opalTestHelper.newEpisode($rootScope);
        // $rootScope.fields = fields;
        // episode = new Episode(angular.copy(episodeData));
    });

    describe("edit item", function(){
      describe("edit item", function(){
          it('should open the EditItemCtrl', function(){
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
              episode.recordEditor.editItem('diagnosis', 1);
              $scope.$digest();
              callArgs = $modal.open.calls.mostRecent().args;
              expect(callArgs.length).toBe(1);
              expect(callArgs[0].controller).toBe('EditItemCtrl');
              expect(callArgs[0].templateUrl).toBe('/templates/modals/diagnosis.html/');
              var resolves = callArgs[0].resolve;
              expect(resolves.item()).toEqual(episode.recordEditor.getItem('diagnosis', 1));
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
              episode.recordEditor.editItem('demographics', 0);
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
              episode.recordEditor.editItem('diagnosis', 0);
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
                episode.recordEditor.editItem('demographics', 0);
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

              episode.recordEditor.editItem('demographics', 0);

              deferred.resolve('save');
              $rootScope.$apply();

              expect($rootScope.state).toBe('normal');
          });

      });

      describe('delete item', function(){
          it('should open the DeleteItemConfirmationCtrl', function(){
                var deferred, callArgs;
                deferred = $q.defer();
                spyOn($modal, 'open').and.returnValue({result: deferred.promise});
                episode.recordEditor.deleteItem('diagnosis', 0);
                $scope.$digest();
                callArgs = $modal.open.calls.mostRecent().args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].controller).toBe('DeleteItemConfirmationCtrl');
                expect(callArgs[0].templateUrl).toBe(
                  '/templates/modals/delete_item_confirmation.html/'
                );
              var resolves = callArgs[0].resolve;
              expect(resolves.item()).toEqual(episode.recordEditor.getItem('diagnosis', 0));
              expect(resolves.profile(null)).toEqual(profile);
            });

            describe('for a readonly user', function(){
                beforeEach(function(){
                    profile.readonly = true;
                });

                it('should return just return an empty promise', function(){
                    var deferred, callArgs;
                    deferred = $q.defer();
                    spyOn($modal, 'open').and.returnValue({result: deferred.promise});
                    episode.recordEditor.deleteItem('diagnosis', 0);
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
                episode.recordEditor.deleteItem('diagnosis', 0);
                deferred.resolve('save');
                $scope.$digest();
            });

            it('should not delete singletons', function(){
              var deferred, callArgs;
              deferred = $q.defer();
              spyOn($modal, 'open').and.returnValue({result: deferred.promise});
              episode.recordEditor.deleteItem('demographics', 0);
              $scope.$digest();
              expect($modal.open.calls.count()).toBe(0);
            });
      });
    });

    describe("get item", function(){
      it("should handle the case where there is no subrecords of this type on the episode", function(){
        var result = episode.recordEditor.getItem("microbiology_test", 0);
        expect(result).not.toBe(undefined);
      });

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

      it('should create an item if no item of that type exists', function(){
        var deferred, callArgs;
        deferred = $q.defer();
        spyOn($modal, 'open').and.returnValue({result: deferred.promise});
        episode.recordEditor.newItem('microbiology_test');
        $scope.$digest();
        callArgs = $modal.open.calls.mostRecent().args;
        expect(callArgs.length).toBe(1);
        expect(callArgs[0].controller).toBe('EditItemCtrl');
        expect(callArgs[0].templateUrl).toBe('/templates/modals/microbiology_test.html/');
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
