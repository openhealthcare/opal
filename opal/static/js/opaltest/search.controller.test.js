describe('SearchCtrl', function (){
    var $scope, location;
    var Episode, Flow;
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
        Episode      = $injector.get('Episode');
        Flow         = $injector.get('Flow');
        $httpBackend = $injector.get('$httpBackend');
        location = $injector.get('$location');
        $window = $injector.get('$window');

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
            profile        : profile,
            PatientSummary: patientSummary
        });

    });});

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });

    describe('We should query for hospital number or name()', function (){
        it('should ask the server for results', function(){
            location.search({
                hospital_number: "Bond",
                name: "Bond",
                page_number: 1
            });

            expectedUrl = "/search/simple/?hospital_number=Bond&name=Bond&page_number=1";
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
            $scope.searchTerm = "Bond";
            $scope.search();
            expectedUrl = "/#/search?hospital_number=Bond&name=Bond";
            expect(locationDetails.href).toEqual(expectedUrl);
        });

        it("should update the url if on the search page", function(){
            locationDetails.href = "unchanged";
            locationDetails.pathname = "/";
            $scope.searchTerm = "Bond";
            $scope.search();
            expectedSearch = {
                hospital_number: "Bond",
                name: "Bond",
            };
            expect(location.search()).toEqual(expectedSearch);
            expect(locationDetails.href).toEqual("unchanged");
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
