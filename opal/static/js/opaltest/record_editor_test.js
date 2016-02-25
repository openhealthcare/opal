describe('RecordEditor', function(){
    "use strict";

    var $scope, $modal;
    var $rootScope, $q, $controller;
    var Flow, Episode, episode;
    var controller;

    var profile = {
        readonly   : false,
        can_extract: true,
        can_see_pid: function(){return true; }
    };

    var options = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy :{'tropical': []}
    }

    var episodeData = {
        id: 123,
        active: true,
        prev_episodes: [],
        next_episodes: [],
        demographics: [{
            id: 101,
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
        module('opal.services', function($provide) {
            $provide.factory('UserProfile', function ($q, $rootScope) {
                var deferred = $q.defer();
                deferred.resolve(profile);
                var profilePromise = deferred.promise;
                return profilePromise;
            });
        });

        inject(function($injector){
            $rootScope = $injector.get('$rootScope');
            $scope = $rootScope.$new();
            $controller = $injector.get('$controller');
            $modal = $injector.get('$modal');
            Episode = $injector.get('Episode');
            $q = $injector.get('$q');
        });

        $rootScope.fields = fields;
        episode = new Episode(angular.copy(episodeData));
    });

    describe("edit item", function(){
      describe("edit item", function(){
          it('should open the EditItemCtrl', function(){
              var deferred, callArgs;
              deferred = $q.defer();
              deferred.resolve();
              var modalPromise = deferred.promise;

              spyOn($modal, 'open').and.returnValue({result: modalPromise}  );
              episode.recordEditor.editItem('demographics', 0);
              $scope.$digest();
              callArgs = $modal.open.calls.mostRecent().args;
              expect(callArgs.length).toBe(1);
              expect(callArgs[0].controller).toBe('EditItemCtrl');
              expect(callArgs[0].templateUrl).toBe('/templates/modals/demographics.html/');
          });

          it('should open the use tags appropriaty', function(){
              var deferred, callArgs;
              deferred = $q.defer();
              deferred.resolve();
              var modalPromise = deferred.promise;

              spyOn($modal, 'open').and.returnValue({result: modalPromise}  );
              episode.recordEditor.editItem('diagnosis', 0, {currentTag: "tropical", currentSubTag: "all"});
              $scope.$digest();
              callArgs = $modal.open.calls.mostRecent().args;
              expect(callArgs.length).toBe(1);
              expect(callArgs[0].controller).toBe('EditItemCtrl');
              expect(callArgs[0].templateUrl).toBe('/templates/modals/diagnosis.html/tropical/all');
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
        episode.recordEditor.newItem('something');
        $scope.$digest();
        callArgs = $modal.open.calls.mostRecent().args;
        expect(callArgs.length).toBe(1);
        expect(callArgs[0].controller).toBe('EditItemCtrl');
        expect(callArgs[0].templateUrl).toBe('/templates/modals/something.html/');
      });

      it('should respond to tags', function(){
        var deferred, callArgs;
        deferred = $q.defer();
        spyOn($modal, 'open').and.returnValue({result: deferred.promise});
        episode.recordEditor.newItem('diagnosis', {currentTag: "tropical", currentSubTag: "all"});
        $scope.$digest();
        callArgs = $modal.open.calls.mostRecent().args;
        expect(callArgs.length).toBe(1);
        expect(callArgs[0].controller).toBe('EditItemCtrl');
        expect(callArgs[0].templateUrl).toBe('/templates/modals/diagnosis.html/tropical/all');
      });
    });
});
