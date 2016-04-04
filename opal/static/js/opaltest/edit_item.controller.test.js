describe('EditItemCtrl', function (){
    "use strict";

    var $scope, $cookieStore, $timeout, $modal, item, Item;
    var dialog, Episode, episode, ngProgressLite, $q;
    var Schema, $modal, $controller, controller, fakeModalInstance;

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
                    {name: 'result', type: 'string'}
                ]
            }
        ]
    };

    var options = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy :{'tropical': []},
        "micro_test_stool_parasitology_pcr": [
            "Stool Parasitology PCR"
        ],
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
            $cookieStore   = $injector.get('$cookieStore');
            $timeout       = $injector.get('$timeout');
            $modal         = $injector.get('$modal');
            ngProgressLite = $injector.get('ngProgressLite');
            Schema         = $injector.get('Schema');
            var $rootScope = $injector.get('$rootScope');
            $scope         = $rootScope.$new();
            $modal         = $injector.get('$modal');
        });

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
            options       : options,
            profile       : profile,
            episode       : episode,
            ngProgressLite: ngProgressLite,
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
            spyOn(item, 'save').and.callFake(function() {
                return deferred.promise;
            });
            expect($scope.saving).toBe(false);
            $scope.save('save');
            expect($scope.saving).toBe(true);
            deferred.resolve("episode returned");
            $scope.$digest();
            expect($scope.saving).toBe(false);
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

});
