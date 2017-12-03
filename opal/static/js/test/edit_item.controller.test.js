describe('EditItemCtrl', function (){
    "use strict";

    var $scope, $timeout, $modal, $httpBackend;
    var item, Item, existingEpisode, opalTestHelper;
    var dialog, Episode, episode, ngProgressLite, $q, $rootScope;
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
            $rootScope = $injector.get('$rootScope');
            $modal         = $injector.get('$modal');
            opalTestHelper = $injector.get('opalTestHelper');
        });

        episode = opalTestHelper.newEpisode($rootScope);
        metadataCopy = opalTestHelper.getMetaData();
        profile = opalTestHelper.getUserProfile();
        referencedata = opalTestHelper.getReferenceData();
        $scope = $rootScope.$new();
        item = new Item(
            {columnName: 'investigation'},
            episode,
            $rootScope.fields.investigation
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
            referencedata: referencedata,
            $analytics: $analytics
        });

    });

    describe('newly-created-controller', function (){
        it('Should have columname investigation', function () {
            expect($scope.columnName).toBe('investigation');
        });
    });

    describe('scope setup', function(){
      it('Should hoist metadata onto the scope', function () {
          expect($scope.metadata).toBe(metadataCopy);
      });

      it('should track analytics data', function(){
          expect($analytics.eventTrack).toHaveBeenCalledWith(
            "investigation", {category: "EditItem", label: "Inpatient"}
          );
      });
    })

    describe('editingMode()', function() {

        it('should know if this is edit or add', function() {
            expect($scope.editingMode()).toBe(false);
        });

    });

    describe('select_macro()', function() {

        it('should return expanded', function() {
            var i = {expanded: 'thing'};
            expect($scope.select_macro(i)).toEqual('thing');
        });

    });

    describe('Saving items', function (){

        it('Should save the current item', function () {
            $scope.$digest();
            var callArgs;
            var deferred = $q.defer();
            spyOn($scope, 'preSave');
            spyOn(item, 'save').and.callFake(function() {
                return deferred.promise;
            });
            $scope.save('save');
            deferred.resolve("episode returned");
            $scope.$digest();

            var preSaveCallArgs = $scope.preSave.calls.mostRecent().args;
            expect(preSaveCallArgs.length).toBe(1);
            expect(preSaveCallArgs[0]).toBe($scope.editing);

            callArgs = item.save.calls.mostRecent().args;
            expect(callArgs.length).toBe(1);
            expect(callArgs[0]).toBe($scope.editing.investigation);
        });

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

    });

    describe('delete()', function() {

        it('should open the delete modal', function() {
            spyOn($modal, 'open');
            $scope.delete();
            expect($modal.open).toHaveBeenCalled()
            var args = $modal.open.calls.mostRecent().args[0];
            expect(args.templateUrl).toEqual('/templates/modals/delete_item_confirmation.html/');
            expect(args.controller).toEqual('DeleteItemConfirmationCtrl');
            expect(args.resolve.item()).toEqual(item)
        });

    });

    describe('cancel()', function(){

        it('should close with null', function(){
            spyOn(fakeModalInstance, 'close');
            $scope.cancel();
            expect(fakeModalInstance.close).toHaveBeenCalledWith('cancel');
        });

    });

    describe('undischarge', function() {
        it('should open the modal', function() {

            spyOn($modal, 'open').and.callFake(function(){
                return {result: {then: function(fn){ fn() }}}
            });;
            $scope.undischarge();
            expect($modal.open).toHaveBeenCalled();
            var resolvers = $modal.open.calls.mostRecent().args[0].resolve
            expect(resolvers.episode()).toEqual(episode);
        });
    });

    describe('prepopulate()', function() {
        it('should extend the item', function() {
            var mock_event = {
                preventDefault: function(){}
            }
            //            $ = jasmine.createSpy().and.callFake(function(what){ console.log(what)})
            var spy = spyOn(jQuery.fn, 'data').and.returnValue({'foo': 'true', 'bar': 'false'});

            $scope.prepopulate(mock_event);
            expect(spy).toHaveBeenCalled();
            expect($scope.editing.investigation.foo).toEqual(true);
            expect($scope.editing.investigation.bar).toEqual(false);
        });
    });

    describe('testType', function(){
        beforeEach(function(){
            existingEpisode = new Episode(opalTestHelper.getEpisodeData());

            // when we prepopulate we should not remove the consistency_token
            existingEpisode.microbiology_test = [{
                test: "T brucei Serology",
                consistency_token: "23423223"
            }];

            item = new Item(
                existingEpisode.microbiology_test[0],
                existingEpisode,
                $rootScope.fields.microbiology_test
            );

            $scope = $rootScope.$new();
            controller = $controller('EditItemCtrl', {
                $scope        : $scope,
                $timeout      : $timeout,
                $modalInstance: fakeModalInstance,
                item          : item,
                metadata      : metadataCopy,
                profile       : profile,
                episode       : existingEpisode,
                ngProgressLite: ngProgressLite,
                referencedata: referencedata,
            });
            // We need to fire the promise - the http expectation is set above.
            $scope.$apply();

        });

        it('on initialisation, update the test type, but not the test details', function(){
          $scope = $rootScope.$new();
          item.test = "C diff";
          item.c_difficile_toxin = "someToxin";
          controller = $controller('EditItemCtrl', {
              $scope        : $scope,
              $timeout      : $timeout,
              $modalInstance: fakeModalInstance,
              item          : item,
              metadata      : metadataCopy,
              profile       : profile,
              episode       : existingEpisode,
              ngProgressLite: ngProgressLite,
              referencedata: referencedata,
          });
          expect($scope.editing.microbiology_test.test).toEqual("C diff");
          expect($scope.editing.microbiology_test.c_difficile_toxin).toEqual("someToxin");
        });

        it("if the test hasn't changed, don't nuke clean other fields", function(){
          $scope.editing.microbiology_test.test = "C diff";
          $scope.$digest();
          expect($scope.editing.microbiology_test.c_difficile_toxin).toEqual("pending");
          $scope.editing.microbiology_test.c_difficile_toxin = "someToxin";
          $scope.editing.microbiology_test.test = "C diff";
          $scope.$digest();
          expect($scope.editing.microbiology_test.c_difficile_toxin).toEqual("someToxin");
        });

        it('should prepopulate microbiology tests', function(){
            $scope.editing.microbiology_test.test = "C diff";
            $scope.$digest();
            expect($scope.editing.microbiology_test.c_difficile_antigen).toEqual("pending");
            expect($scope.editing.microbiology_test.c_difficile_toxin).toEqual("pending");
            $scope.editing.microbiology_test.test = ""
            $scope.$digest();
            expect($scope.editing.microbiology_test.c_difficile_antigen).not.toEqual("pending");
            expect($scope.editing.microbiology_test.c_difficile_toxin).not.toEqual("pending");
            expect($scope.editing.microbiology_test.consistency_token).toEqual("23423223");
        });

        it('should should not clean _client, id, date ordered or episode id', function(){
            var today = moment().format('DD/MM/YYYY');
            $scope.editing.microbiology_test.test = "C diff";
            $scope.editing.microbiology_test.alert_investigation = true;
            $scope.$digest();
            $scope.editing.microbiology_test.c_difficile_antigen = "pending";
            $scope.editing.microbiology_test.episode_id = 1;
            $scope.editing.microbiology_test.id = 2;
            $scope.editing.microbiology_test.date_ordered = today;
            $scope.editing.microbiology_test.consistency_token = "122112";
            $scope.editing.microbiology_test.test = "";
            $scope.editing.microbiology_test._client.something = "important"
            $scope.$digest();
            expect($scope.editing.microbiology_test._client.something).toEqual("important");
            expect($scope.editing.microbiology_test.c_difficile_antigen).not.toEqual("pending");
            expect($scope.editing.microbiology_test.episode_id).toBe(1);
            expect($scope.editing.microbiology_test.id).toBe(2);
            expect($scope.editing.microbiology_test.consistency_token).toBe("122112");
            expect($scope.editing.microbiology_test.date_ordered).toBe(today);
            expect($scope.editing.microbiology_test.alert_investigation).toBe(true);
        });
    });

});
