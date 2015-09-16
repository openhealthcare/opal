describe('EditItemCtrl', function (){
    var $scope, $cookieStore, $timeout, item;
    var dialog, episode, ngProgressLite;

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
                ]},
        ]
    };

    var options = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy :{'tropical': []}
    };

    var profile = {
        readonly   : false,
        can_extract: true,
        can_see_pid: function(){return true; }
    };

    beforeEach(function(){
        module('opal', function($provide) {
            $provide.value('$analytics', function(){
                return {
                    pageTrack: function(x){}
                };
            });

            $provide.provider('$analytics', function(){
                this.$get = function() {
                    return {
                        virtualPageviews: function(x){},
                        settings: {
                            pageTracking: false,
                        },
                        pageTrack: function(x){}
                     };
                };
            });
        });
    });

    beforeEach(function(){
        inject(function($injector){
            $httpBackend = $injector.get('$httpBackend');
            Episode = $injector.get('Episode');
            Item = $injector.get('Item');
            $rootScope   = $injector.get('$rootScope');
            $scope       = $rootScope.$new();
            $controller  = $injector.get('$controller');
            $cookieStore = $injector.get('$cookieStore');
            $modal       = $injector.get('$modal');
            $timeout     = $injector.get('$timeout');
            ngProgressLite   = $injector.get('ngProgressLite');
            Schema   = $injector.get('Schema');
        });

        var schema = new Schema(columns.default);
        episode = new Episode(episodeData);
        item = new Item(
            {columnName: 'diagnosis'},
            episode,
            schema.columns[0]
        );
        dialog = $modal.open({template: 'notarealtemplate!'});

        controller = $controller('EditItemCtrl', {
            $scope      : $scope,
            $cookieStore: $cookieStore,
            $timeout    : $timeout,
            $modalInstance: dialog,
            item        : item,
            options     : options,
            profile     : profile,
            episode     : episode,
            ngProgressLite  : ngProgressLite,
        });

    });

    describe('newly-created-controller', function (){
        it('Should have subtag "all"', function () {
            expect($scope.currentSubTag).toBe('all');
            expect($scope.columnName).toBe('diagnosis');
        });
    });


    describe('Saving items', function (){

        it('Should save the current item', function () {
            var callArgs;
            spyOn(item, 'save').and.callThrough();
            $scope.save('save');
            callArgs = item.save.calls.mostRecent().args;
            expect(callArgs.length).toBe(1);
            expect(callArgs[0]).toBe($scope.editing);
        });
    });
});
