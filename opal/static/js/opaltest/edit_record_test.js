describe('EditRecord', function() {
    "use strict";
    var $modal, recordEditor, rootScope;

    episode = {
        someProperty: ['hello', 'there'];
    }

    beforeEach(function($provide) {
        module('opal.services');
        MockedItem = Object;
        $provide.value('Item', MockedItem);

        inject(function($injector) {
            $modal = $injector.get('$modal');
            RecordEditor = $injector.get('RecordEditor');
            recordEditor = new RecordEditor();
        });
    };

    describe('test delete item', function(){
        it('should not delete read only items', function(){
            self.deleteItem = function(episode, name, iix, rootScope)

        });

        it('should not delete read only items', function(){

        });

        it('should open the delete modal', function(){

        });
    });

    describe('test new item', function(){

    });

    describe('test edit item', function(){

    });
});
