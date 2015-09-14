
describe('ExtractCtrl', function(){
    var $scope, $httpBackend, schema;

    optionsData = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy :{'tropical': []}
    }

    columnsData = [
        {
            "single": true,
            "advanced_searchable": false,
            "readOnly": false,
            "name": "tagging",
            "display_name":"Teams",
            "fields":[
                {"name":"opat","type":"boolean"},
                {"name":"opat_referrals","type":"boolean"},
            ]
        },
        {
            "single":false,
            "name":"demographics",
            "display_name":"Demographics",
            "readOnly": true    ,
            "advanced_searchable": true,
            "fields":[
                {
                    "title":"Consistency Token",
                    "lookup_list":null,
                    "name":"consistency_token",
                    "type":"token"
                },
                {
                    "title":"Name",
                    "lookup_list":null,
                    "name":"name",
                    "type":"string"
                }
            ]
        }
    ];


    beforeEach(function(){
        module('opal.controllers');

        inject(function($injector){
            $httpBackend = $injector.get('$httpBackend');
            $rootScope  = $injector.get('$rootScope');
            $scope      = $rootScope.$new();
            $controller  = $injector.get('$controller');
            $window      = $injector.get('$window');

            Schema = $injector.get('Schema');
            Episode = $injector.get('Episode');
            Item = $injector.get('Item')
        });

        var schema = new Schema(columnsData);

        controller = $controller('ExtractCtrl',  {
            $scope : $scope,
            profile: {},
            options: optionsData,
            filters: [],
            schema : schema
        });
    });

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });

    describe('Getting searchable fields', function(){
        it('should exclude token fields', function(){
            var col = {fields: [
                {name: 'consistency_token', type: 'token'},
                {name: 'hospital', type: 'string'},
            ]}
            expect($scope.searchableFields(col)).toEqual(['Hospital'])
        });
        it('should capitalze the field names', function(){
            var col = {fields: [
                {name: 'hospital_number', type: 'string'},
                {name: 'hospital', type: 'string'},
            ]}
            expect($scope.searchableFields(col)).toEqual(['Hospital Number',
                                                          'Hospital']);
        });
    });

    describe('Search', function(){
        it('should ask the server for results', function(){
            $httpBackend.expectPOST("/search/extract/").respond({
                page_number: 1,
                total_pages: 1,
                total_count: 0
            });
            $scope.search();
            $httpBackend.flush();
        });
    });

    describe('Getting searchable columns', function(){
        it('should only get the columns that are advanced searchable', function(){
            expect($scope.columns).toEqual([columnsData[1]])
        });
    });

});
