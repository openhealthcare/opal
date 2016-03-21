describe('AddEpisodeCtrl', function (){
    var $scope, $httpBackend;
    var modalInstance;
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

    optionsData = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy :{'tropical': []}
    };

    beforeEach(function(){
        module('opal', function($provide) {
            $provide.value('$analytics', function(){
                return {
                    pageTrack: function(x){}
                }
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

    beforeEach(function(){
        var $controller, $modal
        $scope = {};

        inject(function($injector){
            $controller = $injector.get('$controller');
            $modal = $injector.get('$modal');
            $httpBackend = $injector.get('$httpBackend');
            Schema = $injector.get('Schema');
        });

        schema = new Schema(columns.default);
        modalInstance = $modal.open({template: 'Notatemplate'});
        var controller = $controller('AddEpisodeCtrl', {
            $scope: $scope,
            $modalInstance: modalInstance,
            schema: schema,
            options: optionsData,
            demographics: {},
            tags: {tag: 'tropical', subtag: ''}
        });
    });

    describe('initial state', function() {

        it('should know the current tags', function() {
            expect($scope.currentTag).toEqual('tropical');
            expect($scope.currentSubTag).toEqual('');
        });

    });

    describe('Adding an episode', function (){

        it('Should set up the initial editing situation', function () {
            expect($scope.editing.tagging).toEqual([{tropical: true}]);
        });

        it('Should set the subtag to an empty string', function(){
            expect($scope.currentSubTag).toEqual('');
        })
    });

    describe('save()', function(){

        it('should save', function(){
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
            $httpBackend.expectPOST('episode/').respond({demographics:[{patient_id: 1}]})

            $scope.editing.date_of_admission = new Date(13, 1, 2014);
            $scope.editing.demographics.date_of_birth = new Date(13, 1, 1914);
            $scope.save();

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
