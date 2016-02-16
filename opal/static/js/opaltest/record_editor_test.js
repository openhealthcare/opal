describe('RecordEditor', function() {
    "use strict";

    var $modal, recordEditor, rootScope;
    var fields = {};
    var name = "diagnosis";
    var iix = 0;

    var columns = {
        "default": [{
          name: 'diagnosis',
          single: false,
          fields: [
              {name: 'condition', type: 'string'},
              {name: 'provisional', type: 'boolean'},
          ]}
        ]
    };

    episodeData = {
        id: 123,
        active: true,
        prev_episodes: [],
        next_episodes: [],
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

    _.each(columns.default, function(c){
        fields[c.name] = c;
    });


    beforeEach(module('opal.services'));

    beforeEach(function($provide) {
        MockedItem = Object;
        $provide.value('Item', MockedItem);

        inject(function($injector) {
            Schema   = $injector.get('Schema');
            $modal = $injector.get('$modal');
            $q = $injector.get('$q');
            RecordEditor = $injector.get('RecordEditor');
            recordEditor = new RecordEditor(episode);
            Episode = $injector.get('RecordEditor');
            episode = new Episode(episodeData);
            rootScope = $injector.get('$rootScope');
            rootScope.fields = fields;
        });

        var deferred = $q.defer();
        deferred.resolve();
        spyOn($modal, 'open');
        $modal.result = deferred.promise;
    });

    describe('test delete item', function(){
        it('should open the delete modal', function(){
            episode.recordEditor.deleteItem(name, iix, rootScope);
            expect(episode.diagnosis.length).toBe(2);
            expect($modal.open.calls.count()).toBe(1);
            var args = $modal.open.calls.argsFor(0);
            expect(args.controller).toBe('DeleteItemConfirmationCtrl');
            expect(args.templateUrl).toBe('/templates/modals/delete_item_confirmation.html/');
        });

        it('should not delete read only items', function(){
            spyOn(episode.diagnosis, 'isReadOnly').and.returnValue(true);
            episode.recordEditor.deleteItem(name, iix, rootScope);
            expect($modal.open.calls.count()).toBe(0);
        });

        it('should not delete singleton items', function(){
            spyOn(episode.diagnosis, 'isSingleton').and.returnValue(true);
            episode.recordEditor.deleteItem(name, iix, rootScope);
            expect($modal.open.calls.count()).toBe(0);
        });
    });

    describe('test new item', function(){
        

    });

    describe('test edit item', function(){

    });
});
