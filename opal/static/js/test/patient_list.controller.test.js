describe('PatientListCtrl', function() {
    "use strict";
    var episodeData, episodeData2, metaData;
    var Episode, Item, episode, episodeVisibility;
    var profile, episode2;
    var $scope, $cookies, $controller, $q, $httpBackend;
    var $$injector;
    var $location, $routeParams, $http;
    var opalTestHelper;
    var episodedata, controller;
    var $modal, $rootScope;

    var _makecontroller;

    var fakeWindow = {
        location: {href: "dummy"},
        print: function(){}
    }

    var growl = {
        success: jasmine.createSpy()
    }

    beforeEach(function(){
      module('opal.controllers');
      module('opal.test');

      inject(function($injector){
        Episode      = $injector.get('Episode');
        Item         = $injector.get('Item');
        $rootScope   = $injector.get('$rootScope');
        $scope       = $rootScope.$new();
        $cookies     = $injector.get('$cookies');
        $controller  = $injector.get('$controller');
        $q           = $injector.get('$q');
        $modal       = $injector.get('$modal');
        $http        = $injector.get('$http');
        $routeParams = $injector.get('$routeParams');
        $httpBackend = $injector.get('$httpBackend');
        $location    = $injector.get('$location');
        $$injector   = $injector.get('$injector');
        episodeVisibility = $injector.get('episodeVisibility');
        opalTestHelper = $injector.get('opalTestHelper');
      });


        episode = opalTestHelper.newEpisode($rootScope);

        episodeData = opalTestHelper.getEpisodeData();
        episodeData2 = angular.copy(episodeData);
        episodeData2.id = 124;
        episodeData2.demographics[0].first_name = "Suzanne";
        episodeData2.demographics[0].surname = "Vega";
        episode2 = new Episode(episodeData2);

        var deferred = $q.defer();
        deferred.resolve();
        var promise = deferred.promise

        spyOn(episode.recordEditor, 'editItem').and.returnValue(promise);
        spyOn(episode.recordEditor, 'newItem').and.returnValue(promise);
        spyOn($cookies, 'put').and.stub();


        episodedata = {status: 'success', data: {123: episode} };
        episodeVisibility = jasmine.createSpy().and.callFake(episodeVisibility);
        profile = opalTestHelper.getUserProfile();

        metaData = opalTestHelper.getMetaData();
        $routeParams.slug = 'tropical';

        _makecontroller = function(metadata){
            var md = metadata || metaData;
            return $controller('PatientListCtrl', {
                $rootScope       : $rootScope,
                $scope           : $scope,
                $q               : $q,
                $http            : $http,
                $cookies     : $cookies,
                $location        : $location,
                $routeParams     : $routeParams,
                $window          : fakeWindow,
                $injector        : $$injector,
                growl            : growl,
                episodedata      : episodedata,
                profile          : profile,
                metadata         : md,
                episodeVisibility: episodeVisibility
            });
        }

        controller = _makecontroller();

    });

    describe("edit Tags", function(){
        it('should filter an episode if the episode does not have the same tags', function(){
            // imitate the case where we remove all the tags
            $scope.episodes[episode.id] = episode;
            $scope.episodes[episode2.id] = episode2;
            $scope.rows = [episode, episode2];
            var scopeChanged = false;
            $rootScope.$watch("state.modal", function(ca){
                scopeChanged = true;
            });

            $scope.open_modal = function(){};
            spyOn($scope, "open_modal").and.returnValue({then: function(fn){ episode.tagging = [{}]; fn(); }});
            $scope.editTags();
            $scope.$apply();
            expect($scope.rows).toEqual([episode2]);
            expect($scope.episodes[episode.id]).toBe(undefined);
            expect($scope.open_modal).toHaveBeenCalled();
            expect(scopeChanged).toBe(true);
            expect($rootScope.state).toBe("normal");
        });

      describe('should leave the episode if it does have the pertinant tag', function(){
            it('should filter an episode if the episode does not have the same tags', function(){
                // imitate the case where we remove all the tags
                $scope.episodes[episode.id] = episode;
                episode.tagging.micro_orth = true;
                $scope.episodes[episode2.id] = episode2;
                $scope.rows = [episode, episode2];
                $scope.open_modal = function(){};
                spyOn($scope, "open_modal").and.returnValue({then: function(fn){ delete episode.tagging.micro_orth; fn(); }});
                $scope.editTags();
                expect($scope.rows).toEqual([episode, episode2]);
                expect($scope.episodes[episode.id]).toBe(episode);
                expect($scope.open_modal).toHaveBeenCalled();
            });
        });
    });


    describe('newly-created controller', function() {
        it('should have state "normal"', function() {
            expect($rootScope.state).toBe('normal');
        });

        it('should extract single tags', function(){
            expect($scope.currentTag).toBe('tropical');
            expect($scope.currentSubTag).toBe('');
        })

        it('should extract subtags', function() {
            $routeParams.slug = 'inpatients-icu'
            _makecontroller();
            expect($scope.currentTag).toBe('inpatients');
            expect($scope.currentSubTag).toBe('icu');
        });

        it('should set the URL of the last list visited', function() {
            expect($cookies.put).toHaveBeenCalledWith('opal.previousPatientList', 'tropical');
        });

        it('should should set rows and episodes', function() {
            expect(_.keys($scope.episodes)).toEqual(['123']);
            expect($scope.rows.length).toBe(1);
        });

        it('should have no comparators by default', function() {
            expect($scope.comparators).toBe(null);
        });

        it('should load a comparator service if one is set in the metadata', function() {
            spyOn($$injector, 'get').and.returnValue([]);
            var md = angular.copy(metaData)
            md.patient_list_comparators = {tropical: 'TheTropicalCompareService'};
            _makecontroller(md)
            expect($$injector.get).toHaveBeenCalledWith('TheTropicalCompareService');
            expect($scope.comparators).toEqual([]);
        });

    });

    describe('Unknown list', function() {
        it('should redirect to list if set from a cookie', function(){
            spyOn($cookies, "get").and.returnValue('randomlist')
            spyOn($location, 'path');
            spyOn($cookies, 'remove');
            episodedata.status = 'error'
            _makecontroller();
            expect($location.path).toHaveBeenCalledWith('/list/');
            expect($cookies.remove).toHaveBeenCalledWith('opal.previousPatientList');
            expect($cookies.get).toHaveBeenCalledWith('opal.previousPatientList')
        })

        it('should redirect to /404', function() {
            $cookies.remove('opal.previousPatientList');
            episodedata.status = 'error';
            _makecontroller();
            expect(fakeWindow.location.href).toBe("/404");
        });
    });

    describe('_compare', function() {

        it('should use the list comparators if they exist', function() {
            spyOn(episode, 'compare');
            $scope.comparators = [];
            $scope.compareEpisodes(episode, episode2);
            expect(episode.compare).toHaveBeenCalledWith(episode2, [])
        });

    });

  describe('refresh()', function() {
      it('should update .episodes with what the server thinks is the episode', function() {
        var updated = angular.copy(episodeData)
        updated.active = false;

        $httpBackend.expectGET('/api/v0.1/record/').respond({})
        $httpBackend.expectGET('/api/v0.1/episode/123/').respond(updated);
        $scope.refresh(123);

        $httpBackend.flush();
        $rootScope.$apply();

        //
        // We just check against the active property because this means
        // that the object we're accessing has definitely been cycled
        // from the server response
        //
        expect($scope.episodes['123'].active).toBe(false);
        expect($scope.rows[0].active).toEqual(false);
      });

      it('should return a promise that resolves when complete', function(){
        var resolved = false;
        var updated = angular.copy(episodeData)
        updated.active = false;

        $httpBackend.expectGET('/api/v0.1/record/').respond({})
        $httpBackend.expectGET('/api/v0.1/episode/123/').respond(updated);
        $scope.refresh(123).then(function(){
          resolved = true;
        });

        $httpBackend.flush();
        $rootScope.$apply();
        expect(resolved).toBe(true);
      });
  });

    describe('isSelectedEpisode()', function() {
      it('should say yes when given the episode', function() {
            expect($scope.isSelectedEpisode($scope.episode)).toBe(true);
        });

        it('should say no when given not the episode', function() {
            expect($scope.isSelectedEpisode({})).toBe(false);
        });

    });

    describe('jumpToTag()', function() {
        it('should send me to the right path', function() {
            spyOn($location, 'path');
            $scope.jumpToTag('tropical');
            expect($location.path).toHaveBeenCalledWith('/list/tropical');
        });

        describe('for a subtag', function() {
            it('should find the parent tag', function() {
                spyOn($location, 'path');
                $scope.jumpToTag('icu');
                expect($location.path).toHaveBeenCalledWith('/list/inpatients-icu');
            });
        });
    });

    describe('watches', function() {

        beforeEach(function(){
            spyOn($scope, 'getVisibleEpisodes');
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
        });

        it('should call on hosp number', function() {
            $scope.hospital_number = 'goo';
            $rootScope.$apply();
            expect($scope.getVisibleEpisodes).toHaveBeenCalledWith()
        });

        it('should call on ward', function() {
            $scope.ward = 'goo';
            $rootScope.$apply();
            expect($scope.getVisibleEpisodes).toHaveBeenCalledWith()
        });

        it('should call on bed', function() {
            $scope.bed = 'goo';
            $rootScope.$apply();
            expect($scope.getVisibleEpisodes).toHaveBeenCalledWith()
        });

        it('should call on name', function() {
            $scope.name = 'goo';
            $rootScope.$apply();
            expect($scope.getVisibleEpisodes).toHaveBeenCalledWith()
        });
    });

    describe('get visible episodes', function(){
        var episodeData3;

        beforeEach(function(){
            $scope.episodes[episode.id] = episode;
            $scope.episodes[episode2.id] = episode2;
            episodeData3 = angular.copy(episodeData2);
            episodeData3.id = 125;
            episodeData3.demographics[0].first_name = "Suzy";
            episodeData3.demographics[0].surname = "Vega";

            $scope.episodes[episodeData3.id] = new Episode(episodeData3);

            $scope.rows = [
                episode,
                episode2,
                $scope.episodes[episodeData3.id]
            ];

            $scope.episode = episode;
        });

        it('should select the only available episode if there is no episode selected, function()', function(){
          delete $scope.episode;
          episodeVisibility.and.callFake(function(episode){
              return true;
          });
          $scope.getVisibleEpisodes();
          expect($scope.episode.id).toBe(episode.id);
        });


        it('should select the only available episode if filtered to one', function(){
            /*
              so if episode visibility filters out all but one response
              we expect that episode to now be selected
            */
            expect($scope.episode.id).toEqual(episodeData.id);

            episodeVisibility.and.callFake(function(episode){
                return episode.id === episode2.id || episode.id === episodeData3.id;
            });

            $scope.getVisibleEpisodes();

            expect($scope.episode.id).toBe(episode2.id);
        });

        it('should maintain the same episode if its still present', function(){
            /*
              so if episode visibility does not filter
              anything out, we expect the in scope episode to
              be the same
            */
            expect($scope.episode.id).toEqual(episodeData.id);

            episodeVisibility.and.callFake(function(episode){
                return true;
            });

            $scope.getVisibleEpisodes();

            expect($scope.episode.id).toBe(episode.id);
        });

        it('should not call select_episode if the episode is still present', function() {
            expect($scope.episode.id).toEqual(episodeData.id);
            spyOn($scope, 'select_episode');
            episodeVisibility.and.callFake(function(episode){
                return true;
            });
            $scope.getVisibleEpisodes();
            expect($scope.select_episode.calls.count()).toBe(0);
        });

        it('if no episodes are available, keep using the last selected one', function(){
            /*
              so if episode visibility does not filter
              anything out, we expect the in scope episode to
              be the same
            */
            expect($scope.episode.id).toEqual(episodeData.id);

            episodeVisibility.and.callFake(function(episode){
                return false;
            });

            $scope.getVisibleEpisodes();

            expect($scope.episode.id).toBe(episode.id);
        });
    });

    describe('jump to episode detail', function(){

        it('should go to the episode link', function(){
            spyOn($location, 'url');
            $scope.jumpToEpisodeDetail($scope.episode);
            expect($location.url).toHaveBeenCalledWith($scope.episode.link);
        })
    })

    describe('keydown watch', function() {

        it('should open keyboard shortcuts', function() {
            spyOn($scope, 'keyboard_shortcuts');
            $scope.$broadcast('keydown', { keyCode: 191, shiftKey: true });
            expect($scope.keyboard_shortcuts).toHaveBeenCalledWith();
        });

        it('should go to the episode link', function() {
            spyOn($location, 'url');
            $scope.$broadcast('keydown', { keyCode: 13 });
            expect($location.url).toHaveBeenCalledWith($scope.episode.link);
        });

        describe('Moving episode', function() {
            beforeEach(function(){
                $scope.rows.push(episode2)
            });

            it('should go up', function() {
                $scope.rix = 1;
                $scope.$broadcast('keydown', { keyCode: 38 });
                expect($scope.rix).toEqual(0);
            });

            it('should go down', function() {
                expect($scope.rix).toEqual(0);
                $scope.$broadcast('keydown', { keyCode: 40 });
                expect($scope.rix).toEqual(1);
            });

        });

    });

    describe('print()', function() {

        it('should print', function() {
            spyOn(fakeWindow, 'print');
            $scope.print();
            expect(fakeWindow.print).toHaveBeenCalledWith();
        });

    });

    describe('focusOnQuery', function() {

        it('should set state', function() {
            $scope.focusOnQuery();
            expect($scope.state).toEqual('search');
        });

    });

    describe('blurOnQuery', function() {

        it('should set state', function() {
            $scope.blurOnQuery();
            expect($scope.state).toEqual('normal');
        });

    });

    describe('removeFromList', function() {
        it('should remove the episode from the list', function() {
          $scope.removeFromList(123);
          expect($scope.num_episodes).toEqual(0);
        });
    });

    describe('newNamedItem', function(){
        it('should pass through the current scopes tags', function(){
            $scope.newNamedItem(episode, "someName");
            expect(episode.recordEditor.newItem).toHaveBeenCalledWith("someName")
        });
    });

    describe('is_tag_visible_in_list', function() {

        it('should return if the tag is visible', function() {
            expect($scope.is_tag_visible_in_list('tropical')).toEqual(false);
            $scope.metadata.tag_visible_in_list = ['tropical'];
            expect($scope.is_tag_visible_in_list('tropical')).toEqual(true);
        });

    });

    describe('editNamedItem', function() {

        it('should call through to the record editor', function(){
            $scope.editNamedItem($scope.episode, 'demographics', 0);
            expect($scope.episode.recordEditor.editItem).toHaveBeenCalledWith(
                'demographics', $scope.episode.demographics[0]
            );
        });

        it('should re-check visibility if we edit tagging', function() {
            spyOn($scope, 'getVisibleEpisodes');
            $scope.episode.recordEditor.editItem.and.returnValue(
                { then: function(f){ f() }}
            );
            $scope.editNamedItem($scope.episode, 'tagging', 0);
            expect($scope.getVisibleEpisodes).toHaveBeenCalledWith();
        });

        it('should call through to the record editor when we add an item', function() {
            var iix = episodeData.diagnosis.length;
            $scope.editNamedItem($scope.episode, "diagnosis", iix);
            expect($scope.episode.recordEditor.newItem).toHaveBeenCalledWith(
                'diagnosis'
            );
        });
    });

    describe('keyboard_shortcuts()', function() {
        it('should open the modal', function() {
            spyOn($modal, 'open');
            $scope.keyboard_shortcuts()
            expect($modal.open).toHaveBeenCalledWith({
                controller: 'KeyBoardShortcutsCtrl',
                templateUrl: 'list_keyboard_shortcuts.html'
            })
        });
    });

});
