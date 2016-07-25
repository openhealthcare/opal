describe('EditItemCtrl', function (){
    "use strict";

    var $scope, $cookieStore, $timeout, $modal, $httpBackend;
    var item, Item;
    var dialog, Episode, episode, ngProgressLite, $q, $rootScope;
    var Schema, $controller, controller, fakeModalInstance;

    var referencedata = {
        dogs: ['Poodle', 'Dalmation'],
        hats: ['Bowler', 'Top', 'Sun'],
        micro_test_c_difficile: [
            "C diff", "Clostridium difficile"
        ],
        micro_test_stool_parasitology_pcr: [
            "Stool Parasitology PCR"
        ],
        micro_test_defaults: {
            micro_test_c_difficile: {
                c_difficile_antigen: "pending",
                c_difficile_toxin: "pending"
            }
        },
        toLookuplists: function(){return {}}
    };
    var metadata = {
        tag_hierarchy :{'tropical': []},
        micro_test_defaults: {
            micro_test_c_difficile: {
                c_difficile_antigen: "pending",
                c_difficile_toxin: "pending"
            }
        }
    };

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
                ]},
            {
                name:  'investigation',
                single: false,
                fields: [
                    {name: 'result', type: 'string'},
                ]
            },
            {
                name:  'microbiology_test',
                single: false,
                fields: [
                    {name: 'result', type: 'string'},
                    {name: 'consistency_token', type: 'string'},
                    {name: 'test', type: 'string'},
                ]
            }
        ]
    };

    var profile = {
        readonly   : false,
        can_extract: true,
        can_see_pid: function(){return true; }
    };

    beforeEach(module('opal.controllers'));

    beforeEach(function(){
        module(function($provide) {
            $provide.value('UserProfile', function(){ return profile; });
        });

        inject(function($injector){
            Item           = $injector.get('Item');
            Episode        = $injector.get('Episode');
            $controller    = $injector.get('$controller');
            $q             = $injector.get('$q');
            $httpBackend   = $injector.get('$httpBackend');
            $cookieStore   = $injector.get('$cookieStore');
            $timeout       = $injector.get('$timeout');
            $modal         = $injector.get('$modal');
            ngProgressLite = $injector.get('ngProgressLite');
            Schema         = $injector.get('Schema');
            $rootScope = $injector.get('$rootScope');
            $modal         = $injector.get('$modal');
        });

        $rootScope.fields = columns.default;
        $scope = $rootScope.$new();
        var schema = new Schema(columns.default);
        episode = new Episode(episodeData);
        item = new Item(
            {columnName: 'investigation'},
            episode,
            columns['default'][3]
        );

        fakeModalInstance = {
            close: function(){
                // do nothing
            },
        };

        controller = $controller('EditItemCtrl', {
            $scope        : $scope,
            $cookieStore  : $cookieStore,
            $timeout      : $timeout,
            $modalInstance: fakeModalInstance,
            item          : item,
            metadata      : metadata,
            profile       : profile,
            episode       : episode,
            ngProgressLite: ngProgressLite,
            referencedata: referencedata,
        });

    });

    describe('newly-created-controller', function (){
        it('Should have columname investigation', function () {
            expect($scope.columnName).toBe('investigation');
        });
    });

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
    });

    describe('delete()', function() {

        it('should open the delete modal', function() {
            spyOn($modal, 'open');
            $scope.delete();
            expect($modal.open).toHaveBeenCalled()
            var args = $modal.open.calls.mostRecent().args[0];
            expect(args.templateUrl).toEqual('/templates/modals/delete_item_confirmation.html/');
            expect(args.controller).toEqual('DeleteItemConfirmationCtrl');
            expect(args.size).toEqual('lg');
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
            var existingEpisode = new Episode(angular.copy(episodeData));

            // when we prepopulate we should not remove the consistency_token
            existingEpisode.microbiology_test = [{
                test: "T brucei Serology",
                consistency_token: "23423223"
            }];

            item = new Item(
                existingEpisode.microbiology_test[0],
                existingEpisode,
                columns['default'][4]
            );

            $scope = $rootScope.$new();
            controller = $controller('EditItemCtrl', {
                $scope        : $scope,
                $cookieStore  : $cookieStore,
                $timeout      : $timeout,
                $modalInstance: fakeModalInstance,
                item          : item,
                metadata      : metadata,
                profile       : profile,
                episode       : existingEpisode,
                ngProgressLite: ngProgressLite,
                referencedata: referencedata,
            });
            // We need to fire the promise - the http expectation is set above.
            $scope.$apply();

        })

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

        it('should should not clean id, date ordered or episode id', function(){
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
            $scope.$digest();

            expect($scope.editing.microbiology_test.c_difficile_antigen).not.toEqual("pending");
            expect($scope.editing.microbiology_test.episode_id).toBe(1);
            expect($scope.editing.microbiology_test.id).toBe(2);
            expect($scope.editing.microbiology_test.consistency_token).toBe("122112");
            expect($scope.editing.microbiology_test.date_ordered).toBe(today);
            expect($scope.editing.microbiology_test.alert_investigation).toBe(true);
        });
    });

});
