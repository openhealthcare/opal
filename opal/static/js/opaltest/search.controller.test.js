describe('SearchCtrl', function (){
    var $scope, location;
    var Flow;
    var profile, schema, options, locationDetails;
    var patientSummary = {};

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

        $rootScope   = $injector.get('$rootScope');
        $scope       = $rootScope.$new();
        $controller  = $injector.get('$controller');
        Flow         = $injector.get('Flow');
        $httpBackend = $injector.get('$httpBackend');
        location = $injector.get('$location');
        $window = $injector.get('$window');

        schema  = {};
        options = {};
        profile = {};


        spyOn(location, 'path').and.returnValue("/search");

        controller = $controller('SearchCtrl', {
            $scope         : $scope,
            $location      : location,
            Flow: Flow,
            options        : options,
            schema         : schema,
            profile        : profile,
            PatientSummary: patientSummary
        });

    });});

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

            expectedUrl = "/search/simple/?query=Bond&page_number=1";
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
            expectedUrl = "/#/search?query=Bond";
            expect(locationDetails.href).toEqual(expectedUrl);
        });

        it("should update the url if on the search page", function(){
            locationDetails.href = "unchanged";
            locationDetails.pathname = "/";
            $scope.query.searchTerm = "Bond";
            $scope.search();
            expectedSearch = {
                query: "Bond",
            };
            expect(location.search()).toEqual(expectedSearch);
            expect(locationDetails.href).toEqual("unchanged");
        });
    });

    describe("it should autocomplete the search if necessary", function(){
        it('should watch the autocomplete and query if it changes', function(){
          $scope.query.autocompleteSearchTerm = "autocomplete";
          $scope.query.searchTerm = "";
          expectedUrl = "/search/simple/?query=autocomplete";
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
