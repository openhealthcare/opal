describe('SearchCtrl', function (){
    "use strict";

    var $scope, $httpBackend, $window, $rootScope, $controller;
    var location;
    var Flow;
    var profile, schema, options, locationDetails, controller;
    var PatientSummary;

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

    beforeEach(module('opal.controllers'));

    beforeEach(function(){
        locationDetails = {};
        $window = {location: locationDetails };

        module(function($provide) {
            $provide.value('$window', $window);
        });

        inject(function($injector){

            $rootScope     = $injector.get('$rootScope');
            $scope         = $rootScope.$new();
            $controller    = $injector.get('$controller');
            Flow           = $injector.get('Flow');
            PatientSummary = $injector.get('PatientSummary');
            $httpBackend   = $injector.get('$httpBackend');
            location       = $injector.get('$location');
            $window        = $injector.get('$window');

            schema  = {};
            options = {};
            profile = {};


            spyOn(location, 'path').and.returnValue("/search");

            controller = $controller('SearchCtrl', {
                $scope         : $scope,
                $location      : location,
                Flow           : Flow,
                options        : options,
                schema         : schema,
                profile        : profile,
                PatientSummary : PatientSummary
            });

            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({roles: {default: []}});

        });});

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });

    describe('getQueryParam()', function() {

        it('should return autocomplete if there is no searchTerm', function() {
            $httpBackend.expectGET('/search/simple/?query=jane').respond(
                {object_list: [{categories: []}]}
            );
            expect($scope.query.searchTerm.length).toBe(0);
            $scope.query.autocompleteSearchTerm = 'jane';
            expect($scope.getQueryParam()).toEqual('jane');
            $httpBackend.flush();
        });

    });

    describe('setters', function() {

        it('should set state', function() {
            $scope.disableShortcuts();
            expect($scope.state).toEqual('search');
            $httpBackend.flush();
        });

        it('should set state', function() {
            $scope.enableShortcuts();
            expect($scope.state).toEqual('normal');
            $httpBackend.flush();
        });

    });

    describe('Autocomplete selected()', function() {

        it('should set the location', function() {
            $scope.selected({link: '/#/foo/bar'});
            expect($scope.query.autocompleteSearchTerm).toEqual("");
            expect($window.location.href).toEqual('/#/foo/bar');
            $httpBackend.flush();
        });

    });

    describe('We should query for hospital number or name()', function (){
        it('should ask the server for results', function(){
            location.search({
                query: "Bond",
                page_number: 1
            });

            var expectedUrl = "/search/simple/?query=Bond&page_number=1";
            $httpBackend.expectGET(expectedUrl).respond({
                page_number: 1,
                object_list: [],
                total_pages: 1
            });
            $scope.loadResults();
            $httpBackend.flush();
        });

        it("should redirect to the search page if we're not in search", function(){
            locationDetails.href = "";
            locationDetails.pathname = "/somewhere";
            $scope.query.searchTerm = "Bond";
            $scope.search();
            var expectedUrl = "/#/search?query=Bond";
            expect(locationDetails.href).toEqual(expectedUrl);
            $httpBackend.flush();
        });

        it('should take page numbers into account', function() {
            locationDetails.href = "";
            locationDetails.pathname = "/somewhere";
            $scope.query.searchTerm = "Bond";
            $scope.search(3);
            var expectedUrl = "/#/search?page_number=3&query=Bond";
            expect(locationDetails.href).toEqual(expectedUrl);
            $httpBackend.flush();
        });

        it("should update the url if on the search page", function(){
            locationDetails.href = "unchanged";
            locationDetails.pathname = "/";
            $scope.query.searchTerm = "Bond";
            $scope.search();
            var expectedSearch = {
                query: "Bond",
            };
            expect(location.search()).toEqual(expectedSearch);
            expect(locationDetails.href).toEqual("unchanged");
            $httpBackend.flush();
        });
    });

    describe("it should autocomplete the search if necessary", function(){
        it('should watch the autocomplete and query if it changes', function(){
            $scope.query.autocompleteSearchTerm = "autocomplete";
            $scope.query.searchTerm = "";
            var expectedUrl = "/search/simple/?query=autocomplete";
            $httpBackend.expectGET(expectedUrl).respond({
                page_number: 1,
                object_list: [],
                total_pages: 1
            });
            $scope.$apply();
            $httpBackend.flush();
        });
    });

    describe('getEpisodeId', function() {

        it('should use the first episode if we have no active episode_id', function() {
            var patient = {
                episodes: {
                    42: {}, //dummy episode
                    8738: {} // another dummy episode
                }
            }
            expect($scope.getEpisodeID(patient)).toEqual('42');
            $httpBackend.flush();
        });

    });

    describe('jumpToEpisode()', function (){
        it('Should call location.path()', function () {
            $scope.jumpToEpisode({active_episode_id: 555});
            expect(location.path).toHaveBeenCalledWith('/episode/555');
            $httpBackend.flush();
        });
    });

});
