describe('AddEpisodeCtrl', function (){
    var $scope, $httpBackend, $rootScope;
    var modalInstance, mockTagService, tagServiceToSave;
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

    optionsData = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy :{'tropical': []}
    };

    beforeEach(function(){
        module('opal');
        var $controller, $modal
        $scope = {};

        tagServiceToSave = jasmine.createSpy('toSave').and.returnValue({"id_inpatients": true});
        mockTagService = jasmine.createSpy('TagService').and.returnValue(
            {toSave: tagServiceToSave}
        );

        inject(function($injector){
            $controller = $injector.get('$controller');
            $modal = $injector.get('$modal');
            $httpBackend = $injector.get('$httpBackend');
            Schema = $injector.get('Schema');
            $rootScope  = $injector.get('$rootScope');
        });
        $rootScope.fields = angular.copy(columns.default);

        schema = new Schema(columns.default);
        modalInstance = $modal.open({template: 'Notatemplate'});
        var controller = $controller('AddEpisodeCtrl', {
            $scope: $scope,
            $modalInstance: modalInstance,
            schema: schema,
            options: optionsData,
            TagService: mockTagService,
            demographics: {},
            tags: {tag: 'tropical', subtag: ''}
        });
    });

    describe('initial state', function() {
        it('should know the current tags', function() {
            expect(mockTagService).toHaveBeenCalledWith(['tropical']);
        });
    });

    describe('save()', function(){

        it('should save', function(){
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
            $httpBackend.expectPOST('episode/').respond({demographics:[{patient_id: 1}]})
            $scope.editing.date_of_admission = moment(new Date(13, 1, 2014));
            $scope.editing.demographics.date_of_birth = moment(new Date(13, 1, 1914));
            $scope.save();
            expect(tagServiceToSave).toHaveBeenCalled();
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
