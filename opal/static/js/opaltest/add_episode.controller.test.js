describe('AddEpisodeCtrl', function (){
    var $scope;
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
            Schema = $injector.get('Schema');
        });

        schema = new Schema(columns.default);
        dialog = $modal.open({template: 'Notatemplate'});
        var controller = $controller('AddEpisodeCtrl', {
            $scope: $scope,
            $modalInstance: dialog,
            schema: schema,
            options: optionsData,
            demographics: {}
        });
    });

    describe('Adding an episode', function (){

        it('Should set up the initial editing situation', function () {
            expect($scope.editing.tagging).toEqual([{mine: true}]);
        });
    });
});
