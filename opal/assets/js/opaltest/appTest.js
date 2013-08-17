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

		$httpBackend.whenGET('/schema/').respond([]);
		$httpBackend.whenGET('/options/').respond([]);
		$httpBackend.whenGET('/templates/patient_list.html').respond();
		$httpBackend.whenGET('/templates/patient_detail.html').respond();
		$httpBackend.whenGET('/templates/search.html').respond();
	});

	describe('request to /', function() {
		it('should load PatientListCtrl', function() {
			$location.path('/');
			$rootScope.$apply();

			expect($route.current.templateUrl).toBe('/templates/patient_list.html');
			expect($route.current.controller).toBe('PatientListCtrl');
		});
	});

	describe('request to /patient/123', function() {
		it('should load PatientDetailCtrl', function() {
			$location.path('/patient/123');
			$rootScope.$apply();

			expect($route.current.templateUrl).toBe('/templates/patient_detail.html');
			expect($route.current.controller).toBe('PatientDetailCtrl');
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
