describe('SearchCtrl', function (){
    var $scope, location;
    var Episode, Flow;
    var profile, schema, options;

    beforeEach(function(){
        module('opal', function($provide) {
            $provide.value('$analytics', function(){
                return {
                    pageTrack: function(x){}
                }
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

    beforeEach(function(){ module('opal.controllers') });

    beforeEach(inject(function($injector){
        $rootScope   = $injector.get('$rootScope');
        $scope       = $rootScope.$new();
        $controller  = $injector.get('$controller');
        location     = $injector.get('$location');
        Episode      = $injector.get('Episode');
        Flow         = $injector.get('Flow');
        $httpBackend = $injector.get('$httpBackend');
        $location = $injector.get('$location');

        $location.search({
            hospital_number: "Bond",
            name: "Bond",
            page_number: 1
        })

        schema  = {};
        options = {};
        profile = {};


        controller = $controller('SearchCtrl', {
            $scope         : $scope,
            $location      : location,
            Episode: Episode,
            Flow: Flow,

            options        : options,
            schema         : schema,
            profile        : profile
        });

    }));

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });

    describe('We should query for hospital number or name()', function (){
        it('should ask the server for results', function(){
            expectedUrl = "/search/simple/?hospital_number=Bond&name=Bond&page_number=1";
            $httpBackend.expectGET(expectedUrl).respond({
                page_number: 1,
                object_list: [],
                total_pages: 1
            });
            $scope.loadResults();
            $httpBackend.flush();
        });
    });

    describe('jumpToEpisode()', function (){
        it('Should call location.path()', function () {
            spyOn(location, 'path').and.callThrough();
            $scope.jumpToEpisode({active_episode_id: 555});
            expect(location.path).toHaveBeenCalledWith('/episode/555');
        });
    });

});
