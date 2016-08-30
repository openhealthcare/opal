describe('SearchCtrl', function (){
    "use strict";
    var $scope, location, controller;
    var Flow;
    var profile, schema, options;
    var patientSummary = {};
    var $rootScope, $httpBackend, fakeWindow;

    beforeEach(module('opal.controllers'));

    beforeEach(function(){
      inject(function($injector){
        $rootScope   = $injector.get('$rootScope');
        $scope       = $rootScope.$new();
        var $controller  = $injector.get('$controller');
        Flow         = $injector.get('Flow');
        $httpBackend = $injector.get('$httpBackend');
        location = $injector.get('$location');

        schema  = {};
        options = {};
        profile = {};

        spyOn(location, 'path').and.returnValue("/search");
        fakeWindow = {location: {pathname: undefined}};

        controller = $controller('SearchCtrl', {
            $scope         : $scope,
            $window        : fakeWindow,
            $location      : location,
            Flow: Flow,
            options        : options,
            schema         : schema,
            profile        : profile,
            PatientSummary: patientSummary
        });

      });
    });

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });

    describe('setters', function() {

        it('should set state', function() {
            $scope.disableShortcuts();
            expect($scope.state).toEqual('search');
        });

        it('should set state', function() {
            $scope.enableShortcuts();
            expect($scope.state).toEqual('normal');
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
            fakeWindow.location.href = ""
            fakeWindow.location.pathname = "/somewhere";
            $scope.query.searchTerm = "Bond";
            $scope.search();
            var expectedUrl = "/#/search?query=Bond";
            expect(fakeWindow.location.href).toEqual(expectedUrl);
        });

        it("should update the url if on the search page", function(){
            fakeWindow.location.href = "unchanged";
            fakeWindow.location.pathname = "/";
            $scope.query.searchTerm = "Bond";
            $scope.search();
            var expectedSearch = {
                query: "Bond",
            };
            expect(location.search()).toEqual(expectedSearch);
            expect(fakeWindow.location.href).toEqual("unchanged");
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


    describe('jumpToEpisode()', function (){
        it('Should call location.path()', function () {
            $scope.jumpToEpisode({active_episode_id: 555});
            expect(location.path).toHaveBeenCalledWith('/episode/555');
        });
    });

});
