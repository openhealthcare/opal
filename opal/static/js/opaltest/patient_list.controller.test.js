describe('PatientListCtrl', function() {
    "use strict";
    var episodeData, episodeData2, optionsData, patientData, Schema;
    var schema, Episode, Item, episode;
    var profile;
    var $scope, $cookieStore, $controller, $q, $dialog, $httpBackend;
    var $location, $routeParams, $http;
    var Flow;
    var episodedata, controller;
    var $modal, options, $rootScope;

    var _makecontroller;

    var fakeWindow = {
        location: {href: "dummy"},
        print: function(){}
    }

    var fields = {};
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
                ]},
            {
                name: 'tagging',
                single: true,
                fields: [
                    {name: 'mine', type: 'boolean'},
                    {name: 'tropical', type: 'boolean'}
                ]
            }
        ]
    };

    _.each(columns.default, function(c){
        fields[c.name] = c;
    });

    episodeData = {
        id: 123,
        active: true,
        prev_episodes: [],
        next_episodes: [],
        demographics: [{
            id: 101,
            patient_id: 99,
            first_name: 'John',
            surname: 'Smith'
        }],
        tagging: [{'mine': true, 'tropical': true}],
        location: [{
            category: 'Inepisode',
            hospital: 'UCH',
            ward: 'T10',
            bed: '15',
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

    optionsData = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy: {'tropical': [], 'inpatients': ['icu']},
        tag_display: {'tropical': 'Tropical', 'icu': "ICU"},
        tags: {
            opat_referrals: {
                display_name: "OPAT Referral",
                parent_tag: "opat",
                name: "opat_referrals"
            },
            tropical: {
                display_name: "Tropical",
                name: "tropical"
            },
            mine: {
              direct_add: true,
              display_name: 'Mine',
              name: 'mine',
              slug: 'mine'
            },
            icu: {
              direct_add: true,
              display_name: 'ICU',
              name: 'icu',
              slug: 'icu'
          }
        }
    };

    profile = {
        can_edit: function(x){
            return true;
        },
        readonly   : false,
        can_extract: true,
        can_see_pid: function(){return true; }
    };

    var growl = {
        success: jasmine.createSpy()
    }

    beforeEach(module('opal.controllers'));

    beforeEach(inject(function($injector){
        Schema   = $injector.get('Schema');
        Episode  = $injector.get('Episode');
        Item     = $injector.get('Item');
        $rootScope   = $injector.get('$rootScope');
        $scope       = $rootScope.$new();
        $cookieStore = $injector.get('$cookieStore');
        $controller  = $injector.get('$controller');
        $q           = $injector.get('$q');
        $modal       = $injector.get('$modal');
        $http        = $injector.get('$http');
        $routeParams = $injector.get('$routeParams');
        $httpBackend = $injector.get('$httpBackend');
        $location    = $injector.get('$location');
        Flow         = $injector.get('Flow');

        schema = new Schema(columns.default);
        $rootScope.fields = fields;

        episodeData2 = angular.copy(episodeData);
        episodeData2.id = 124;
        episode = new Episode(episodeData)

        var deferred = $q.defer();
        deferred.resolve();
        var promise = deferred.promise

        spyOn(episode.recordEditor, 'deleteItem').and.returnValue(promise);
        spyOn(episode.recordEditor, 'editItem').and.returnValue(promise);
        spyOn($cookieStore, 'put').and.callThrough();

        episodedata = {status: 'success', data: {123: episode} };

        options = optionsData;
        $routeParams.slug = 'tropical';

        _makecontroller = function(){
            return $controller('PatientListCtrl', {
                $rootScope    : $rootScope,
                $scope        : $scope,
                $q            : $q,
                $http         : $http,
                $cookieStore  : $cookieStore,
                $location     : $location,
                $routeParams  : $routeParams,
                $window       : fakeWindow,
                growl         : growl,
                Flow          : Flow,
                schema        : schema,
                episodedata   : episodedata,
                profile       : profile,
                options       : options,
                viewDischarged: false
            });
        }

        controller = _makecontroller();

    }));

    describe('newNamedItem', function(){
        it('should pass through the current scopes tags', function(){
          spyOn(episode.recordEditor, "newItem");
          $scope.newNamedItem(episode, "someName");
          expect(episode.recordEditor.newItem).toHaveBeenCalledWith("someName")
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
            expect($cookieStore.put).toHaveBeenCalledWith('opal.lastPatientList', 'tropical');
        });

        it('should should set rows and episodes', function() {
            expect(_.keys($scope.episodes)).toEqual(['123']);
            expect($scope.rows.length).toBe(1);
        });

    });

    describe('Unknown list', function() {

        it('should redirect to list if set from a cookie', function(){
            $cookieStore.put('opal.lastPatientList', 'randomlist');
            spyOn($location, 'path');
            spyOn($cookieStore, 'remove');
            episodedata.status = 'error'
            _makecontroller();
            expect($location.path).toHaveBeenCalledWith('/list/');
            expect($cookieStore.remove).toHaveBeenCalledWith('opal.lastPatientList');
        })

        it('should redirect to /404', function() {
            $cookieStore.remove('opal.lastPatientList');
            episodedata.status = 'error';
            _makecontroller();
            expect(fakeWindow.location.href).toBe("/404");
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

        it('should go up', function() {
            $scope.$broadcast('keydown', { keyCode: 38 });
        });

        it('should go up', function() {
            $scope.$broadcast('keydown', { keyCode: 40 });
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


    describe('adding an episode', function() {
        var fake_episode_resolver = function(){
            return {then : function(fn){ fn(new Episode(episodeData2)) }};
        };

        it('should call flow', function() {
            spyOn(Flow, 'enter').and.callFake(fake_episode_resolver);
            $scope.addEpisode();
            expect(Flow.enter).toHaveBeenCalledWith(options, {current_tags: {
                tag: $scope.currentTag,
                subtag: $scope.currentSubTag
            }})
        });

        it('should allow the enter flow to resolve with a promise', function() {
            $scope.currentTag = 'mine';
            spyOn(Flow, 'enter').and.callFake(
                function(){
                    return {
                        then : function(fn){ fn({
                            then: function(fn){ fn(new Episode(episodeData) ) }
                        })}
                    }
                }
            );
            $scope.addEpisode();
            expect(Flow.enter).toHaveBeenCalledWith(options, {current_tags: {
                tag: $scope.currentTag,
                subtag: $scope.currentSubTag
            }});

            expect(growl.success).toHaveBeenCalledWith('John Smith added to the Mine list');
        });

        it('should print the correct message even dependent on the current tag', function(){
          $scope.currentTag = 'tropical';
          spyOn(Flow, 'enter').and.callFake(
              function(){
                  return {
                      then : function(fn){ fn({
                          then: function(fn){ fn(new Episode(episodeData) ) }
                      })}
                  }
              }
          );
          $scope.addEpisode();
          expect(growl.success).toHaveBeenCalledWith('John Smith added to the Tropical list');
        });

        it('should print the correct message even in the case of multiple tags with hierarchies on the current tag', function(){
          $scope.currentTag = 'opat';
          $scope.currentSubTag = 'opat_referrals';
          var episodeData3 = angular.copy(episodeData);
          episodeData3.tagging = [
              {opat: true, opat_referrals: true, mine: true}
          ];
          spyOn(Flow, 'enter').and.callFake(
              function(){
                  return {
                      then : function(fn){ fn({
                          then: function(fn){ fn(new Episode(episodeData3) ) }
                      })}
                  }
              }
          );
          $scope.addEpisode();
          expect(growl.success).toHaveBeenCalledWith('John Smith added to the OPAT Referral list');
        });

        it('should add the new episode to episodes if it has the current tag', function() {
            spyOn(Flow, 'enter').and.callFake(fake_episode_resolver);
            expect($scope.rows.length).toBe(1);
            $scope.addEpisode();
            expect($scope.rows.length).toBe(2);
        });

        it('should not add the new episode to episodes if it does not have the current tag', function() {
            episodeData2.tagging = [{'mine': true, 'id_inpatients': true}];
            spyOn(Flow, 'enter').and.callFake(fake_episode_resolver);
            expect($scope.rows.length).toBe(1);
            $scope.addEpisode();
            expect($scope.rows.length).toBe(1);
        });

        describe('for a readonly user', function(){
            beforeEach(function(){
                profile.readonly = true;
            });

            it('should return null', function(){
                expect($scope.addEpisode()).toBe(null);
            });

            afterEach(function(){
                profile.readonly = false;
            });
        });
    });

    describe('discharging an episode', function(){
        describe('_post_discharge()', function (){

            beforeEach(function(){
                $rootScope.state = 'modal'
            });

            it('Should set the $scope.state', function () {
                $scope._post_discharge();
                expect($rootScope.state).toBe('normal');
            });

            it('Should re-set the visible episodes', function () {
                spyOn($scope, 'getVisibleEpisodes').and.callThrough();
                $scope._post_discharge('discharged', episode);
                expect($scope.getVisibleEpisodes).toHaveBeenCalledWith();
            });

            it('Should re-set the focus to 0', function () {
                /*
                 * reselect the first episode available when we discharge
                 */
                spyOn($scope, 'select_episode');
                $scope.episodes[episodeData2.id] = new Episode( episodeData2 );
                $scope._post_discharge('discharged', episode);
                var first_name = $scope.select_episode.calls.allArgs()[0][0].demographics[0].first_name;
                var surname = $scope.select_episode.calls.allArgs()[0][0].demographics[0].surname;
                expect(first_name).toEqual("John");
                expect(surname).toEqual("Smith");
            });
        });

        describe('should discharge', function() {

            var fake_exit = function(){
                return {
                    then: function(fn){
                        fn('discharged');
                    }
                }
            }

            beforeEach(function(){
                $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
            });

            it('should discharge the patient', function() {
                spyOn(Flow, 'exit').and.callFake(fake_exit);
                $scope.dischargeEpisode(episode);
                $rootScope.$apply();
            });

            it('should should discharge the patient if flow returns a promise', function() {
                var fake_exit = function(){
                    return {
                        then: function(fn){
                            fn({ then: function(gn){ gn() } } );
                        }
                    }
                }
                spyOn(Flow, 'exit').and.callFake(fake_exit);
                $scope.dischargeEpisode(episode);
                $rootScope.$apply();
            });

            describe('for multiple patients', function() {
                beforeEach(function(){
                    var episodeData3 = angular.copy(episodeData);
                    episodeData3.id = 125
                    episodedata = {
                        status: 'success',
                        data: {
                            123: episode,
                            124: new Episode(episodeData2),
                            125: new Episode(episodeData3)
                        }
                    };
                    _makecontroller()
                });

                it('should remove the episode from episodes', function() {
                    spyOn(Flow, 'exit').and.callFake(fake_exit);
                    expect(_.keys($scope.episodes).length).toBe(3);
                    $scope.dischargeEpisode(episode);
                    $rootScope.$apply();
                    expect(_.keys($scope.episodes).length).toBe(2);
                });

                it('should set a new active episode', function() {
                    spyOn(Flow, 'exit').and.callFake(fake_exit);
                    expect($scope.rix).toEqual(0);
                    expect($scope.episode.id).toEqual(123);
                    expect($scope.rows.length).toEqual(3)
                    $scope.dischargeEpisode(episode);
                    $rootScope.$apply();

                    expect($scope.rix).toEqual(0);
                    expect($scope.rows.length).toEqual(2)
                    expect($scope.episode.id).toEqual(124);
                });


            });

        });

        describe('for a readonly user', function(){
            beforeEach(function(){
                profile.readonly = true;
            });

            it('should return null', function(){
                expect($scope.dischargeEpisode(0)).toBe(null);
            });

            afterEach(function(){
                profile.readonly = false;
            });
        });
    });

    describe('removeFromMine()', function() {

        it('should be null if readonly', function() {
            profile.readonly = true;
            expect($scope.removeFromMine(0, null)).toBe(null);
        });

        it('should remove the mine tag', function() {
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
            profile.readonly = false;
            var mock_event = {preventDefault: jasmine.createSpy()};
            $scope.removeFromMine(0, mock_event);
            $rootScope.$apply();
            $httpBackend.flush();
        });

    });

    describe('editing an item', function() {
        it('should call through to the record editor', function(){
            $scope.editNamedItem($scope.episode, 'demographics', 0);
            expect($scope.episode.recordEditor.editItem).toHaveBeenCalledWith(
                'demographics', 0
            );
        });
    });

    describe('adding an item', function() {
        var iix;

        beforeEach(function() {
            iix = episodeData.diagnosis.length;
        });

        it('should call through to the record editor', function() {
            $scope.editNamedItem($scope.episode, "diagnosis", iix);
            expect($scope.episode.recordEditor.editItem).toHaveBeenCalledWith(
                'diagnosis', iix
            );
        });
    });


});
