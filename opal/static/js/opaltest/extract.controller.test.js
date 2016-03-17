describe('ExtractCtrl', function(){
    "use strict";

    var $scope, $httpBackend, schema, $window, Item;
    var PatientSummary;

    var optionsData = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy :{'tropical': []}
    }

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
                },
                {
                    "title": "Deceased",
                    "lookup_list": null,
                    "name": "dead",
                    "type": "boolean"
                },
                {
                    "title": "Date of Birth",
                    "lookup_list": null,
                    "name": "date_of_birth",
                    "type": "date"
                }
            ]
        },
        {
            "single": false,
            "name": "symptoms",
            "display_name": "Symptoms",
            "readOnly": false,
            "advanced_searchable": true,
            "fields": [
                {
                    "title": "Symptoms",
                    "lookup_list": "symptoms",
                    "name": "symptoms",
                    "type": "many_to_many"
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
            PatientSummary = $injector.get('PatientSummary');
            Item = $injector.get('Item')
        });

        var schema = new Schema(columnsData);

        controller = $controller('ExtractCtrl',  {
            $scope : $scope,
            profile: {},
            options: optionsData,
            filters: [],
            schema : schema,
            PatientSummary: PatientSummary
        });
    });

    describe('Getting Complete Criteria', function(){

        it('should be true if we have a query', function(){
            $scope.criteria[0].column = 'demographics';
            $scope.criteria[0].field = 'name';
            $scope.criteria[0].queryType = 'contains';
            $scope.criteria[0].query = 'jane';
            expect($scope.completeCriteria().length).toBe(1);
        });

        it('should be false if we have no query', function(){
            $scope.criteria[0].column = 'demographics';
            $scope.criteria[0].field = 'name';
            $scope.criteria[0].queryType = 'contains';
            expect($scope.completeCriteria().length).toBe(0);
        });

        it('tagging should always be true', function(){
            $scope.criteria[0].column = 'tagging';
            $scope.criteria[0].field = 'Inpatients';
            expect($scope.completeCriteria().length).toBe(1);
        });

    })

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

        it('should special case Micro Test fields', function(){
            var expected = [
                'Test',
                'Date Ordered',
                'Details',
                'Microscopy',
                'Organism',
                'Sensitive Antibiotics',
                'Resistant Antibiotics'
            ];
            expect($scope.searchableFields({name: 'microbiology_test'})).toEqual(expected);
        });

        it('should filter out timestamp fields', function(){
            var col = {fields: [
                {name: 'created', type: 'date'},
                {name: 'hospital', type: 'string'},
            ]}
            expect($scope.searchableFields(col)).toEqual(['Hospital'])
        });

    });

    describe('Checking field type', function(){

        it('should be falsy for non fields', function(){
            expect($scope.isType()).toBe(false);
        });

        it('should be falsy for nonexistent fields', function(){
            expect($scope.isType("demographics", "towel_preference")).toBe(false);
        });

        it('should find boolean fields', function(){
            expect($scope.isBoolean("Demographics", "dead")).toEqual(true);
        });

        it('should find string fields', function(){
            expect($scope.isText("Demographics", "name")).toBe(true);
        });

        it('should find select fields', function(){
            expect($scope.isSelect("Symptoms", "symptoms")).toBe(true);
        });

        it('should find date fields', function(){
            expect($scope.isDate("Demographics", "date_of_birth")).toBe(true);
        });

    });

    describe('addFilter()', function(){

        it('should add a criteria', function(){
            expect($scope.criteria.length).toBe(1);
            $scope.addFilter();
            expect($scope.criteria.length).toBe(2);
        });

    });

    describe('removeFilter()', function(){

        it('should always leave 1 filter', function(){
            expect($scope.criteria.length).toBe(1);
            $scope.removeFilter();
            expect($scope.criteria.length).toBe(1);
        });

        it('should remove a criteria', function(){
            $scope.addFilter();
            expect($scope.criteria.length).toBe(2);
            $scope.removeFilter();
            expect($scope.criteria.length).toBe(1);
        });

    });

    describe('resetFilter()', function(){

        it('should reset the criteria', function(){
            $scope.criteria[0].field = "demographics";
            $scope.criteria[0].column = "name";
            $scope.criteria[0].combine = "or";
            $scope.criteria[0].query = "Jane";
            $scope.criteria[0].queryType = "contains";
            $scope.resetFilter(0, ["combine", "field"]);
            expect($scope.criteria[0].combine).toEqual("or");
            expect($scope.criteria[0].field).toEqual("demographics");
            expect($scope.criteria[0].column).toEqual(null);
            expect($scope.criteria[0].query).toEqual(null);
            expect($scope.criteria[0].queryType).toEqual(null);
        })

    });

    describe('removeCriteria', function(){

        it('should reset the criteria', function(){
            $scope.criteria.push('hello world');
            $scope.removeCriteria();
            expect($scope.criteria.length).toBe(1);
        });

    });

    describe('_lookuplist_watch', function(){

        it('should set the lookuplist', function(){
            $scope.symptoms_list = ['thing']
            $scope.criteria[0].column = "symptoms";

            $scope.criteria[0].field = 'symptoms';
            $scope._lookuplist_watch();
            expect($scope.criteria[0].lookup_list).toEqual(['thing']);
        });

    });

    describe('Search', function(){
        beforeEach(function(){
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({roles: {default: []}});
        });

        it('should ask the server for results', function(){
            $httpBackend.expectPOST("/search/extract/").respond({
                page_number: 1,
                total_pages: 1,
                total_count: 0,
                object_list: [
                    {categories: []}
                ]
            });
            $scope.criteria[0] = {
                combine    : "and",
                column     : "symptoms",
                field      : "symptoms",
                queryType  : "contains",
                query      : "cough",
                lookup_list: []
            }
            $scope.search();
            if(!$rootScope.$$phase) {
                $rootScope.$apply();
            }
            $httpBackend.flush();
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
        });

        it('should handle errors', function(){
            spyOn($window, 'alert');
            $httpBackend.expectPOST('/search/extract/').respond(500, {});
            $scope.search();
            $httpBackend.flush();
            expect($window.alert).toHaveBeenCalled();
        });

    });

    describe('Getting searchable columns', function(){
        it('should only get the columns that are advanced searchable', function(){
            expect($scope.columns).toEqual([columnsData[1], columnsData[2]])
        });
    });

});
