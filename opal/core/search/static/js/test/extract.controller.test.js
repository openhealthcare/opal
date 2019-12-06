describe('ExtractCtrl', function(){
    "use strict";

    var $scope, $httpBackend, schema, $window, $timeout, $modal, Item;
    var PatientSummary, $controller, Schema, controller, $rootScope;
    var ExtractSchema;

    var optionsData = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy :{'tropical': []}
    };

    var pulledInData = {
      dogs: ['Poodle', 'Dalmation'],
      hats: ['Bowler', 'Top', 'Sun']
    };

    var referencedata = {
      dogs: ['Poodle', 'Dalmation'],
      hats: ['Bowler', 'Top', 'Sun'],
      toLookuplists: function(){
        return {
          dogs_list: ['Poodle', 'Dalmation'],
          hats_list: ['Bowler', 'Top', 'Sun']
        };
      }
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
                    "title": "Age",
                    "lookup_list": null,
                    "name": "age",
                    "type": "integer"
                },
                {
                    "title": "Date of Birth",
                    "lookup_list": null,
                    "name": "date_of_birth",
                    "type": "date"
                },
                {
                    "title": "Last Appointment",
                    "lookup_list": null,
                    "name": "last_appointment",
                    "type": "date_time"
                },
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
                },
                {
                    "title":"Consistency Token",
                    "lookup_list":null,
                    "name":"consistency_token",
                    "type":"token"
                },
                {
                    "title":"Created",
                    "lookup_list":null,
                    "name":"created",
                    "type":"date_time"
                }
            ]
        },
    ];

    beforeEach(function(){
        module('opal');
    });

    beforeEach(function(){
        inject(function($injector){
            $httpBackend = $injector.get('$httpBackend');
            $rootScope  = $injector.get('$rootScope');
            $scope      = $rootScope.$new();
            $window      = $injector.get('$window');
            $modal       = $injector.get('$modal');
            $timeout     = $injector.get('$timeout');
            $controller  = $injector.get('$controller');
            ExtractSchema = $injector.get('ExtractSchema');
            PatientSummary = $injector.get('PatientSummary');
            Item = $injector.get('Item');
        });

        var extractSchema = new ExtractSchema(columnsData);

        var controller = $controller('ExtractCtrl',  {
            $scope : $scope,
            $modal: $modal,
            profile: {},
            options: optionsData,
            filters: [],
            extractSchema : extractSchema,
            PatientSummary: PatientSummary,
            referencedata: referencedata
        });

        // $httpBackend.expectGET('/api/v0.1/userprofile/').respond({roles: {default: []}});
        $scope.$apply();
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });

    describe('set up', function(){
      it('should set up any or all options', function(){
        expect($scope.combinations).toEqual(["all", "any"]);
      });

      it('should set up any or all default', function(){
        expect($scope.anyOrAll).toBe("all");
      });
    });

    describe('Getting Complete Criteria', function(){

        it('should be true if we have a query', function(){
            $scope.criteria[0].column = 'demographics';
            $scope.criteria[0].field = 'surname';
            $scope.criteria[0].query = 'jane';
            expect($scope.completeCriteria().length).toBe(1);
        });

        it('should allow queries for False', function(){
          $scope.criteria[0].column = 'demographics';
          $scope.criteria[0].field = 'dead';
          $scope.criteria[0].query = false;
          expect($scope.completeCriteria().length).toBe(1);
        });

        it('should allow queries for 0', function(){
          $scope.criteria[0].column = 'demographics';
          $scope.criteria[0].field = 'age';
          $scope.criteria[0].query = 0;
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

        it("should update the critieria to or if we're of anyOrAll is 'any'", function(){
          $scope.anyOrAll = "any";
          $scope.completeCriteria();
          expect($scope.criteria[0].combine).toBe('or');
        });

        it("should update the critieria to and if we're of anyOrAll is 'all'", function(){
          $scope.anyOrAll = "all";
          $scope.completeCriteria();
          expect($scope.criteria[0].combine).toBe('and');
        });
    });

    describe('Getting searchable fields', function(){


        it('should exclude token and not advanced searchable fields', function(){
          var symptomsExpected = {
            title: 'Symptoms',
            lookup_list: 'symptoms',
            name: 'symptoms',
            type: 'many_to_many'
          };

          expect($scope.searchableFields('symptoms')).toEqual([symptomsExpected]);
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
            expect($scope.isBoolean("demographics", "dead")).toEqual(true);
        });

        it('should find string fields', function(){
            expect($scope.isText("demographics", "name")).toBe(true);
        });

        it('should find select fields', function(){
            expect($scope.isSelect("symptoms", "symptoms")).toBe(true);
        });

        it('should find date fields', function(){
            expect($scope.isDate("demographics", "date_of_birth")).toBe(true);
        });

        it('should find number fields', function(){
            expect($scope.isNumber("demographics", "age")).toBe(true);
        });

        it('should find date time fields', function(){
            expect($scope.isDateTime("demographics", "last_appointment")).toBe(true);
        });

        it('should find date type fields', function(){
            expect($scope.isDateType("demographics", "date_of_birth")).toBe(true);
        });
    });

    describe('Find Field', function(){
        it('should return the field', function(){
          expect(!!$scope.findField("demographics", "dead")).toEqual(true);
        });
    });

    describe('addFilter()', function(){

        it('should add a criteria', function(){
            expect($scope.criteria.length).toBe(1);
            $scope.addFilter();
            expect($scope.criteria.length).toBe(2);
        });

    });

    describe('readableQuery()', function(){
        it('should return null if its handed a null', function(){
          // we hand the function null if we're looking at tagging
          expect($scope.readableQuery(null)).toBe(null);
        });

        it('should lower case the result', function(){
          expect($scope.readableQuery('Contains')).toBe('contains');
        });

        it('should add "is" as a prefix for time queries', function(){
          expect($scope.readableQuery('Before')).toBe('is before');
          expect($scope.readableQuery('After')).toBe('is after');
        });

        it('should change equals to "is"', function(){
          expect($scope.readableQuery('Equals')).toBe('is');
        });
    });

    describe('removeFilter()', function(){

        it('should always leave an empty filter', function(){
            expect($scope.criteria.length).toBe(1);
            $scope.removeFilter();
            expect($scope.criteria.length).toBe(1);
            expect($scope.criteria[0].column).toBe(null);
        });

        it('should remove a criteria', function(){
            $scope.addFilter();
            expect($scope.criteria.length).toBe(2);
            $scope.removeFilter();
            expect($scope.criteria.length).toBe(1);
        });

    });

    describe('resetFilter()', function(){
        var criteria;
        beforeEach(function(){
          criteria = {
            column: "demographics",
            field: "name",
            query: "Jane",
            queryType: "contains"
          };
        });

        it('should reset the column', function(){

            $scope.resetFilter(criteria, ['column']);
            expect(criteria.column).toEqual("demographics");
            expect(criteria.field).toEqual(null);
            expect(criteria.query).toEqual(null);
            expect(criteria.queryType).toEqual(null);
        });

        it('should reset the field', function(){
            $scope.resetFilter(criteria, ['column', 'field']);
            expect(criteria.column).toEqual("demographics");
            expect(criteria.field).toEqual("name");
            expect(criteria.query).toEqual(null);
            expect(criteria.queryType).toEqual(null);
        });

        it('should empty the selectedInfo', function(){
            $scope.selectedInfo = "some info";
            $scope.resetFilter(criteria, ['column']);
            expect($scope.selectedInfo).toBe(undefined);
        });
    });

    describe('removeCriteria', function(){
        it('should reset the criteria', function(){
            $scope.criteria.push('hello world');
            $scope.removeCriteria();
            expect($scope.criteria.length).toBe(1);
        });
    });

    describe('getChoices', function(){
        it('should get a lookup list and suffix it', function(){
            spyOn($scope, "findField").and.returnValue({
              lookup_list: "dogs"
            });
            var result = $scope.getChoices("some", "field");
            expect(result).toEqual(['Poodle', 'Dalmation']);
        });

        it('should get an enum', function(){
          spyOn($scope, "findField").and.returnValue({
            enum: [1, 2, 3]
          });
          var result = $scope.getChoices("some", "field");
          expect(result).toEqual([1, 2, 3]);
        });
    });

    describe('refresh', function(){
        it('should reset the searched critera', function(){
            $scope.searched = true;
            $scope.refresh();
            expect($scope.searched).toBe(false);
        });

        it('should reset async waiting', function(){
          $scope.async_waiting = true;
          $scope.refresh();
          expect($scope.async_waiting).toBe(false);
        });

        it('should reset async ready', function(){
          $scope.async_ready = true;
          $scope.refresh();
          expect($scope.async_ready).toBe(false);
        });

        it('should clean the results', function(){
          $scope.results = [{something: "interesting"}];
          $scope.refresh();
          expect($scope.results).toEqual([]);
        });
    });

    describe('Search', function(){
        it('should ask the server for results', function(){
            $httpBackend.expectPOST("/search/extract/").respond({
                page_number: 1,
                total_pages: 1,
                total_count: 0,
                object_list: [
                    {categories: []}
                ]
            });
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({roles: {default: []}});
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
            expect($scope.searched).toBe(true);
        });

        it('should handle errors', function(){
            spyOn($window, 'alert');
            $httpBackend.expectPOST('/search/extract/').respond(500, {});
            $scope.criteria[0] = {
                combine    : "and",
                column     : "symptoms",
                field      : "symptoms",
                queryType  : "contains",
                query      : "cough",
                lookup_list: []
            }
            $scope.search();
            $httpBackend.flush();
            expect($window.alert).toHaveBeenCalled();
        });

        it('should handle not send a search if there are no criteria', function(){
            $scope.search();
            expect($scope.searched).toBe(true);
            $httpBackend.verifyNoOutstandingExpectation();
        });
    });

    describe('async_extract', function() {

        it('should open a new window if async_ready', function() {
            $scope.async_ready = true;
            $scope.extract_id = '23';
            spyOn($window, 'open');
            $scope.async_extract();

            expect($window.open).toHaveBeenCalledWith('/search/extract/download/23', '_blank');
        });

        it('should return null if async_waiting', function() {
            $scope.async_waiting = true;
            expect($scope.async_extract()).toBe(null);
        });

        it('should post to the url', function() {
            $httpBackend.expectPOST('/search/extract/download').respond({extract_id: '23'});
            $httpBackend.expectGET('/search/extract/result/23').respond({state: 'SUCCESS'})
            $scope.async_extract();
            $timeout.flush()
            $rootScope.$apply();
            $httpBackend.flush();

            expect($scope.extract_id).toBe('23');
            $rootScope.$apply();

            expect($scope.async_ready).toBe(true);
        });

        it('should re-ping', function() {
            $httpBackend.expectPOST('/search/extract/download').respond({});
            $scope.async_extract();
            $timeout.flush()
            $rootScope.$apply();
            $httpBackend.flush();
            $timeout.flush()
        });

        it('should re-ping if we are pending', function(){
            $httpBackend.expectPOST('/search/extract/download').respond({extract_id: '349'});
            var status_counter = 0;
            var status_responder = function(){
                if(status_counter == 0){
                    status_counter ++;
                    return [200, {state: 'PENDING'}]
                }
                return [200, {state: 'SUCCESS'}];
            }
            $httpBackend.when('GET', '/search/extract/result/349').respond(status_responder)
            $scope.async_extract();
            $timeout.flush()
            $rootScope.$apply();
            $httpBackend.flush();

            $timeout.flush()
            $rootScope.$apply();
            $httpBackend.flush();
            expect($scope.async_ready).toBe(true);
        });

        it('should alert if we fail', function() {
            $httpBackend.expectPOST('/search/extract/download').respond({extract_id: '23'});
            $httpBackend.expectGET('/search/extract/result/23').respond({state: 'FAILURE'})
            spyOn($window, 'alert');
            $scope.async_extract();
            $timeout.flush()
            $rootScope.$apply();
            $httpBackend.flush();

            expect($scope.extract_id).toBe('23');
            $rootScope.$apply();

            expect($scope.async_ready).toBe(false);
            expect($window.alert).toHaveBeenCalledWith('FAILURE');

        });

    });

    describe('jumpToFilter()', function() {

        it('should reset the criteria', function() {
            var mock_default = jasmine.createSpy();
            var mock_event = {preventDefault: mock_default};
            $scope.jumpToFilter(mock_event, {criteria: []});
            expect($scope.criteria).toEqual([]);
            expect(mock_default).toHaveBeenCalledWith();
        });

    });

    describe('editFilter()', function() {

        it('should open the modal', function() {
            spyOn($modal, 'open').and.returnValue({result: {then: function(f){f()}}});
            var mock_default = jasmine.createSpy();
            var mock_event = {preventDefault: mock_default};
            $scope.filters = [{}]
            $scope.editFilter(mock_event, {}, 0);
            expect($modal.open).toHaveBeenCalled();
        });

        it('should pass the params', function() {
            spyOn($modal, 'open').and.returnValue({result: {then: function(f){f()}}});
            var mock_default = jasmine.createSpy();
            var mock_event = {preventDefault: mock_default};
            $scope.editFilter(mock_event, {}, 0);
            var resolves = $modal.open.calls.mostRecent().args[0].resolve;
            expect(resolves.params()).toEqual($scope.filters[0]);
        });

    });

    describe('Getting searchable columns', function(){
        it('should only get the columns that are advanced searchable', function(){
            expect($scope.columns).toEqual([
              columnsData[1], columnsData[2]
            ]);
        });
    });

    describe('save()', function() {

        it('should save() the data', function() {
            spyOn($modal, 'open').and.returnValue({result: {then: function(f){f()}}});
            $scope.save();
            expect($modal.open).toHaveBeenCalled();
        });

        it('should pass the params', function() {
            spyOn($modal, 'open').and.returnValue({result: {then: function(f){f()}}});
            $scope.save();
            var resolves = $modal.open.calls.mostRecent().args[0].resolve;
            expect(resolves.params()).toEqual({name: null, criteria: $scope.completeCriteria()});
        });

    });

});
