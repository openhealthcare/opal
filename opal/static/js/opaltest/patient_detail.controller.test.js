describe('PatientDetailCtrl', function(){
    "use strict";

    var $scope, $rootScope, $controller, $modal, $routeParams, $httpBackend;
    var Flow;
    var patient;
    var controller;
    var episodeData = {
        id: 123,
        active: true,
        prev_episodes: [],
        next_episodes: [],
        demographics: [{
            id: 101,
            patient_id: 99,
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
    var metadata = {some: "metadata"};

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

    var profile = {
        readonly   : false,
        can_extract: true,
        can_see_pid: function(){return true; }
    };

    var options = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy :{'tropical': []}
    }

    beforeEach(function(){
        module('opal');

        inject(function($injector){
            $rootScope   = $injector.get('$rootScope');
            $scope       = $rootScope.$new();
            $controller  = $injector.get('$controller');
            $modal       = $injector.get('$modal');
            $routeParams = $injector.get('$routeParams');
            $httpBackend = $injector.get('$httpBackend');
            Episode      = $injector.get('Episode');
        });

        $rootScope.fields = fields
        patient = {episodes: [new Episode(angular.copy(episodeData))] };

        Flow = {exit: jasmine.createSpy().and.returnValue({then: function(fn){ fn() }}) };

        controller = $controller('PatientDetailCtrl', {
            $scope      : $scope,
            $routeParams: $routeParams,
            Flow        : Flow,
            patient     : patient,
            options     : options,
            profile     : profile,
            metadata    : metadata
        });

    });

    describe('initialization', function(){

        it('should set up state', function(){
            expect($scope.patient).toEqual(patient)
        });

        it('should call switch_to_view', function() {
            spyOn($scope, 'switch_to_view');
            $routeParams.view = 'myview';
            $scope.initialise();
            expect($scope.switch_to_view).toHaveBeenCalledWith('myview');
        });

        it('should set the episode', function() {
            spyOn($scope, 'switch_to_episode');
            $routeParams.view = '123';
            $scope.initialise();
            expect($scope.switch_to_episode).toHaveBeenCalledWith(0);
        });

        it('should hoist the metaddata', function(){
            expect($scope.metadata.some).toBe('metadata');
        });
    });

    describe('switch_to_episode()', function() {

        it('should switch to the episode', function() {
            var mock_event = {preventDefault: jasmine.createSpy()};
            $scope.switch_to_episode(0, mock_event);
            expect($scope.view).toBe(null);
            expect($scope.episode).toBe(patient.episodes[0]);
        });

    });

    describe('switch_to_view()', function() {

        it('should switch', function() {
            $scope.switch_to_view('wat');
            expect($scope.view).toEqual('wat');
        });

    });

    describe('dischargeEpisode()', function() {

        it('should should return null if readonly', function() {
            profile.readonly = true;
            expect($scope.dischargeEpisode()).toBe(null);
        });

        it('should call Flow.', function() {
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
            profile.readonly = false;
            $scope.dischargeEpisode();
            $rootScope.$apply();
        });

    });

});
