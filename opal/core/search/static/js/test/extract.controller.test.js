describe('ExtractCtrl', function(){
    "use strict";

    var $scope, $httpBackend, schema, $window, $timeout, $modal, Item;
    var PatientSummary, $controller, ExtractSchema, controller, $rootScope;
    var extractSchema, Schema;

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
            "single":false,
            "name":"demographics",
            "display_name":"Demographics",
            "readOnly": true    ,
            "fields":[
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
                    "default": null,
                    "description": null,
                    "enum": null,
                    "lookup_list": "gender",
                    "model": "Demographics",
                    "name": "sex",
                    "title": "Sex",
                    "type": "string"
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
            "fields": [
                {
                    "title": "Symptoms",
                    "lookup_list": "symptoms",
                    "name": "symptoms",
                    "type": "many_to_many"
                },
                {
                    "title":"Created",
                    "lookup_list":null,
                    "name":"created",
                    "type":"date_time"
                }
            ]
        }
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
            Schema = $injector.get('Schema');
            PatientSummary = $injector.get('PatientSummary');
            Item = $injector.get('Item');
        });

        var extractSchema = new ExtractSchema(angular.copy(columnsData));
        var dataDictionary = new Schema(angular.copy(columnsData));

        var controller = $controller('ExtractCtrl',  {
            $scope : $scope,
            $modal: $modal,
            profile: {},
            filters: [],
            extractSchema : extractSchema,
            PatientSummary: PatientSummary,
            referencedata: referencedata,
            dataDictionary: dataDictionary
        });

        $scope.$apply();
    });

    describe('set up', function(){
      it('should default the page state to query', function(){
        expect($scope.state).toBe('query');
      });

      it('should put reference data on the scope', function(){
        expect($scope.referencedata).toBe(referencedata);
      });

      it('should set up the schema on the scope', function(){
        expect(!!$scope.extractSchema.columns).toBe(true);
      });

      it('should set the selected info', function(){
        expect($scope.sliceSubrecord.name).toBe('demographics');
      });

      it('should set the fieldInfo', function(){
        expect($scope.fieldInfo.name).toBe('name');
      });

      it('should put the extract schema on the scope', function(){
        expect(!!$scope.dataDictionary.columns).toBe(true);
      });

      it('should put filters on the scope', function(){
        expect(!!$scope.filters).toBe(true);
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

        it('should call through to reset the column', function(){
            spyOn($scope.extractQuery, 'resetFilter');
            $scope.resetFilter(criteria, ['column']);
            expect($scope.extractQuery.resetFilter).toHaveBeenCalledWith(
              criteria, ['column']
            )
        });

        it('should change the selected info', function(){
            $scope.selectedInfo = "some info";
            $scope.resetFilter(criteria, ['column']);
            expect($scope.selectedInfo).toBe(criteria);
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

    describe('getQueryParams', function(){
      it('should get the critera and the page number', function(){
          var criteria = [{
              combine    : "and",
              column     : "symptoms",
              field      : "symptoms",
              queryType  : "contains",
              query      : "cough",
              lookup_list: []
          }];
          $scope.extractQuery.criteria = criteria;
          var expected = angular.copy(criteria);
          expected[0]["page_number"] = 1;
          expect($scope.getQueryParams(1)).toEqual(expected);
      });

      it('should remove the hash key', function(){
          var expected = [{
              combine    : "and",
              column     : "symptoms",
              field      : "symptoms",
              queryType  : "contains",
              query      : "cough",
              lookup_list: [],
          }];

          var criteria = angular.copy(expected);
          criteria["%%hashKey"] = 123;
          $scope.extractQuery.criteria = criteria;
          var expected = angular.copy(criteria);
          expected[0]["page_number"] = 1;
          expect($scope.getQueryParams(1)).toEqual(expected);
      });

      it('should copy the criteria', function(){
        var criteria = [{
            combine    : "and",
            column     : "symptoms",
            field      : "symptoms",
            queryType  : "contains",
            query      : "cough",
            lookup_list: []
        }];
        $scope.extractQuery.criteria = criteria;
        criteria[0].page_number = 1;
        expect($scope.getQueryParams(1)).toEqual(criteria);
        expect($scope.getQueryParams(1)).not.toBe(criteria);
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
            $scope.extractQuery.criteria[0] = {
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

        it('should not replace the search results if they have subsequently been updated the criteria', function(){
            $httpBackend.expectPOST("/search/extract/").respond({
                page_number: 1,
                total_pages: 1,
                total_count: 0,
                object_list: [
                    {
                      categories: [],
                      first_name: "Wilma"
                    }
                ]
            });

            $scope.extractQuery.criteria[0] = {
                combine    : "and",
                column     : "symptoms",
                field      : "symptoms",
                queryType  : "contains",
                query      : "cough",
                lookup_list: []
            };

            $scope.search();

            $scope.extractQuery.criteria[0] = {
                combine    : "and",
                column     : "diagnosis",
                field      : "condition",
                queryType  : "contains",
                query      : "cough",
                lookup_list: []
            };

            $httpBackend.flush();
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
            // the results should not be updated because the query has changed
            expect($scope.results.length).toBe(0);
        });

        it('should handle errors', function(){
            spyOn($window, 'alert');
            $httpBackend.expectPOST('/search/extract/').respond(500, {});
            $scope.extractQuery.criteria[0] = {
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
            $httpBackend.expectGET('/search/extract/status/23').respond({state: 'SUCCESS'})
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
            $httpBackend.when('GET', '/search/extract/status/349').respond(status_responder)
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
            $httpBackend.expectGET('/search/extract/status/23').respond({state: 'FAILURE'})
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

        it('should query with a data slice', function(){
          $scope.extractQuery.criteria = [{
            "column": "demographics",
            "field": "first_name",
            "queryType":"Contains",
            "query":"a",
            "combine":"and"
          }];
          spyOn($scope.extractQuery, "getDataSlices").and.returnValue([{
            "demographics": ["first_name", "surname"]
          }]);

          var expected = {
            criteria: JSON.stringify([{
              "column": "demographics",
              "field": "first_name",
              "queryType":"Contains",
              "query":"a",
              "combine":"and"
            }]),
            data_slice: JSON.stringify([{
              "demographics": ["first_name", "surname"]
            }])
          };

          $httpBackend.expectPOST('/search/extract/download', expected).respond({extract_id: '23'});
          $httpBackend.expectGET('/search/extract/status/23').respond({state: 'SUCCESS'})

          $scope.async_extract(true);
          $timeout.flush()
          $rootScope.$apply();
          $httpBackend.flush();

          expect($scope.extract_id).toBe('23');
          $rootScope.$apply();

          expect($scope.async_ready).toBe(true);
        });
    });

    describe('jumpToFilter()', function() {

        it('should reset the criteria', function() {
            var mock_default = jasmine.createSpy();
            var mock_event = {preventDefault: mock_default};
            $scope.jumpToFilter(mock_event, {criteria: []});
            expect($scope.extractQuery.criteria).toEqual([]);
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
            expect(resolves.params()).toEqual({name: null, criteria: $scope.extractQuery.completeCriteria()});
        });
    });

    describe('selectSliceSubrecord', function(){
      it('should select the slice subrecord', function(){
        $scope.selectSliceSubrecord("something");
        expect($scope.sliceSubrecord).toBe("something");
      });
    });

    describe('setFieldInfo', function(){
      it('should set the field info', function(){
        $scope.setFieldInfo("something");
        expect($scope.fieldInfo).toBe("something");
      });
    });
});
