
describe('ExtractCtrl', function(){
    "use strict";

    var $scope, $httpBackend, schema, $window, Item;

    var optionsData = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy :{'tropical': []}
    }

    var patientSummary = {};

    var columnsData = [
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
        inject(function($injector){
            $httpBackend = $injector.get('$httpBackend');
            $rootScope  = $injector.get('$rootScope');
            $scope      = $rootScope.$new();
            $window      = $injector.get('$window');
            $controller  = $injector.get('$controller');
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
            schema : schema,
            PatientSummary: patientSummary
        });
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
            ]};
            expect($scope.searchableFields(col)).toEqual(['Hospital', 'Hospital Number']);
        });
    });

    describe('Search', function(){
        beforeEach(function(){
            $httpBackend.expectPOST("/search/extract/").respond({
                page_number: 1,
                total_pages: 1,
                total_count: 0
            });
        });

        it('should ask the server for results', function(){
            $scope.search();
            if(!$rootScope.$$phase) {
                $rootScope.$apply();
            }
            $httpBackend.flush();
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
        });
    });

    describe('Getting searchable columns', function(){
        it('should only get the columns that are advanced searchable', function(){
            expect($scope.columns).toEqual([columnsData[1]])
        });
    });

});
