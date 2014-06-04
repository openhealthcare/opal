describe('app', function() {
    var $location, $route, $rootScope, $httpBackend;

    beforeEach(function() {
        module('opal');
        inject(function($injector) {
            $location = $injector.get('$location');
            $route = $injector.get('$route');
            $rootScope = $injector.get('$rootScope');
            $httpBackend = $injector.get('$httpBackend');

        });

        $httpBackend.whenGET('/schema/list/').respond([]);
        $httpBackend.whenGET('/schema/detail/').respond([]);
        $httpBackend.whenGET('/options/').respond([]);
        $httpBackend.whenGET('/userprofile/').respond([]);
        $httpBackend.whenGET('/templates/episode_list.html').respond();
        $httpBackend.whenGET('/templates/episode_detail.html').respond();
        $httpBackend.whenGET('/templates/search.html').respond();
    });

    describe('request to /', function() {
        it('should load EpisodeListCtrl', function() {
            $location.path('/list/micro');
            $httpBackend.whenGET('/templates/episode_list.html/micro').respond();
            $rootScope.$apply();
            expect($route.current.controller).toBe('EpisodeListCtrl');
        });
    });

    describe('request to /episode/123', function() {
        it('should load EpisodeDetailCtrl', function() {
            $location.path('/episode/123');
            $rootScope.$apply();

            expect($route.current.templateUrl).toBe('/templates/episode_detail.html');
            expect($route.current.controller).toBe('EpisodeDetailCtrl');
        });
    });

    describe('request to /search', function() {
        it('should load SearchCtrl', function() {
            $location.path('/search');
            $rootScope.$apply();

            expect($route.current.templateUrl).toBe('/templates/search.html');
            expect($route.current.controller).toBe('SearchCtrl');
        });
    });
});
