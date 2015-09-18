describe('EpisodeDetailCtrl', function(){
    var $scope, $cookieStore, $modal;
    var Flow;
    var episode;

    var profile = {
        readonly   : false,
        can_extract: true,
        can_see_pid: function(){return true; }
    };

    var options = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy :{'tropical': []}
    }

    episodeData = {
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
    var fields = {}
    _.each(columns.default, function(c){
        fields[c.name] = c;
    });

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
            $rootScope   = $injector.get('$rootScope');
            $scope       = $rootScope.$new();
            $q           = $injector.get('$q');
            $controller  = $injector.get('$controller');
            $cookieStore = $injector.get('$cookieStore');
            $modal       = $injector.get('$modal');
        });

        $rootScope.fields = fields
        episode = new Episode(episodeData);
        Flow = jasmine.createSpy('Flow').and.callFake(function(){return {then: function(){}}});

        controller = $controller('EpisodeDetailCtrl', {
            $scope      : $scope,
            $modal      : $modal,
            $cookieStore: $cookieStore,
            Flow        : Flow,
            episode     : episode,
            options     : options,
            profile     : profile
        });
    });

    describe('initialization', function(){
        it('should set up state', function(){
            expect($scope.episode).toEqual(episode);
        });
    });

    describe('selecting an item', function(){
        it('should select the item', function(){
            $scope.selectItem(1, 34);
            expect($scope.cix).toBe(1);
            expect($scope.iix).toBe(34);
        });
    })

    describe('editing an item', function(){
        it('should open the EditItemCtrl', function(){
            var deferred, callArgs;

            deferred = $q.defer();
            spyOn($modal, 'open').and.returnValue({result: deferred.promise});

            $scope.editNamedItem('demographics', 0);

            callArgs = $modal.open.calls.mostRecent().args;
            expect(callArgs.length).toBe(1);
            expect(callArgs[0].controller).toBe('EditItemCtrl');
        });

        describe('for a readonly user', function(){
            beforeEach(function(){
                profile.readonly = true;
            });

            it('should return null', function(){
                expect($scope.editNamedItem('demographics', 0)).toBe(null);
            });

            afterEach(function(){
                profile.readonly = false;
            });
        });

    });

    describe('deleting an item', function(){
        it('should open the DeleteItemConfirmationCtrl', function(){
            var deferred, callArgs;

            deferred = $q.defer();
            spyOn($modal, 'open').and.returnValue({result: deferred.promise});

            $scope.deleteItem('diagnosis', 0);

            callArgs = $modal.open.calls.mostRecent().args;
            expect(callArgs.length).toBe(1);
            expect(callArgs[0].controller).toBe('DeleteItemConfirmationCtrl');
        });

        describe('for a readonly user', function(){
            beforeEach(function(){
                profile.readonly = true;
            });

            it('should return null', function(){
                expect($scope.deleteItem('diagnosis', 0)).toBe(null);
            });

            afterEach(function(){
                profile.readonly = false;
            });
        });

    });

    describe('discharging an episode', function(){
        var mockEvent;

        beforeEach(function(){
            mockEvent = {preventDefault: function(){}};
        });

        it('should call the exit flow', function(){
            $scope.dischargeEpisode(mockEvent);
            expect(Flow).toHaveBeenCalledWith(
                'exit', null, options,
                {
                    current_tags: {
                        tag   : undefined,
                        subtag: undefined
                    },
                    episode: episode

                }
            );
        });

        describe('for a readonly user', function(){
            beforeEach(function(){
                profile.readonly = true;
            });

            it('should return null', function(){
                expect($scope.dischargeEpisode(mockEvent)).toBe(null);
            });

            afterEach(function(){
                profile.readonly = false;
            });
        });
    });

});
