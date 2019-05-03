describe('app', function() {
    "use strict";

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
        $httpBackend.whenGET('/templates/patient_lists/layouts/spreadsheet_list.html').respond();
        $httpBackend.whenGET('/templates/episode_detail.html').respond();
        $httpBackend.whenGET('/search/templates/search.html').respond();
    });


});
