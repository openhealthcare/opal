describe('UndischargeCtrl', function() {
    "use strict";

    var $rootScope, $scope, $httpBackend, $modal, $window, $controller;
    var Episode, opalTestHelper;
    var modalInstance, episode, episodeData;

    episodeData = {
        id: 221,
        demographics: [{patient_id: 1234}],
        location: [{id: 12}]
    };

    var columns = {
        "default": [
            {
                name: 'demographics',
                single: true,
                fields: [
                    {name: 'first_name', type: 'string'},
                    {name: 'surname', type: 'string'},
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

    beforeEach(function(){
        module('opal.controllers');
        module('opal.test');

        inject(function($injector){
            $httpBackend = $injector.get('$httpBackend');
            $rootScope   = $injector.get('$rootScope');
            $scope       = $rootScope.$new();
            $controller  = $injector.get('$controller');
            $modal       = $injector.get('$modal');
            $window      = $injector.get('$window');
            Episode      = $injector.get('Episode');
            opalTestHelper = $injector.get('opalTestHelper');
        });

        $rootScope.fields = fields;
        modalInstance = $modal.open({template: 'notatemplate'});

        // episode = new Episode(episodeData);
        episode = opalTestHelper.newEpisode($rootScope);

        $controller('UndischargeCtrl', {
            $scope        : $scope,
            $modalInstance: modalInstance,
            episode       : episode
        });
    });

    describe('confirm', function() {
        it('should confirm', function() {
            $httpBackend.expectPUT('/api/v0.1/episode/123/').respond(episodeData);
            $httpBackend.expectPUT('/api/v0.1/location/12/').respond({});
            $scope.confirm();
            $rootScope.$apply();
            $httpBackend.flush();
        });

    });

    describe('cancel()', function(){

        it('should close with null', function(){
            spyOn(modalInstance, 'close');
            $scope.cancel();
            expect(modalInstance.close).toHaveBeenCalledWith(null);
        });

    });

});
