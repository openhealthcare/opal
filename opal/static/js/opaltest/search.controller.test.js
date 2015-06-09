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

    
    describe('jumpToEpisode()', function (){

        it('Should call location.path()', function () {
            spyOn(location, 'path').andCallThrough();
            $scope.jumpToEpisode({id: 555});
            expect(location.path).toHaveBeenCalledWith('/episode/555');
        });

    });
    
});
