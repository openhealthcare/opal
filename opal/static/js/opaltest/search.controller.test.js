describe('SearchCtrl', function (){
    var $scope, location;
    var Episode, Flow;
    var profile, schema, options;

    beforeEach(function(){ module('opal.controllers') });

    beforeEach(inject(function($injector){

        $rootScope   = $injector.get('$rootScope');
        $scope       = $rootScope.$new();
        $controller  = $injector.get('$controller');
        location     = $injector.get('$location');
        Episode      = $injector.get('Episode');
        Flow         = $injector.get('Flow');
        $httpBackend = $injector.get('$httpBackend');

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
        it('should ask the server for results', function(done){
            expectedUrl = "/search/simple/?hospital_number=Bond&name=Bond&page_number=1";
            $httpBackend.expectGET(expectedUrl).respond({
                page_number: 1,
                object_list: [],
                total_pages: 1
            });
            $scope.searchTerm = "Bond";
            $scope.search();
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
