describe('ExtractQuery', function(){
  "use strict";

  var ExtractQuery, extractQuery, schema;

  beforeEach(function(){
    module('opal.services');
    inject(function($injector){
      ExtractQuery = $injector.get('ExtractQuery');
    });
    schema = jasmine.createSpyObj(["findField"]);
    var createFakeSubrecord = function(y, x){

      return {
        name: x,
        subrecord: {name: y}
      }
    };
    schema.findField.and.callFake(createFakeSubrecord);
    extractQuery = new ExtractQuery(schema);
  });

  describe('setUp', function(){
    it('should set up any or all options', function(){
      expect(extractQuery.combinations).toEqual(["all", "any"]);
    });

    it('should set up any or all default', function(){
      expect(extractQuery.anyOrAll).toBe("all");
    });

    it('should setUp required extract fields', function(){
      expect(extractQuery.requiredExtractFields).toEqual([
        {name: "date_of_birth", subrecord: {name: "demographics"}},
        {name: "sex", subrecord: {name: "demographics"}},
      ]);
    });
  });

  describe('addSubrecordSlices', function(){
    it('should add all fields for a subrecord', function(){
      extractQuery.slices = [];
      extractQuery.addSlice("someField");

      var someSubrecord = {
        fields: [
          "someField", "someOtherField"
        ]
      }
      extractQuery.addSubrecordSlices(someSubrecord);
      var expected = ["someField", "someOtherField"];
      var found = _.clone(extractQuery.slices);
      expect(found).toEqual(expected);
    });
  });

  describe('addSlice()', function(){
    it('should add a field to the slice', function(){
      extractQuery.addSlice("someField");
      expect(_.last(extractQuery.slices)).toEqual("someField");
    });

    it('should not add a field to the slice if the field already exists', function(){
      // a single slice should only be allowed to be added once.
      extractQuery.addSlice("someField");
      var expected = _.clone(extractQuery.slices);
      extractQuery.addSlice("someField");
      var found = _.clone(extractQuery.slices);
      expect(found).toEqual(expected);
    });

  });

  describe('sliceIsRequired()', function(){
    it('should be true if the slice is required', function(){
      var required = extractQuery.requiredExtractFields[0];
      expect(extractQuery.sliceIsRequired(required)).toBe(true);
    });

    it('should be false if the slice is not required', function(){
      var required = extractQuery.requiredExtractFields[0];
      expect(extractQuery.sliceIsRequired(required)).toBe(true);
    });
  });

  describe('isSliceAdded()', function(){
    it('should be true if the slice is added', function(){
      extractQuery.addSlice("something");
      expect(extractQuery.isSliceAdded("something")).toBe(true);
    });

    it('should be false if the slice is added', function(){
      extractQuery.addSlice("something else");
      expect(extractQuery.isSliceAdded("something")).toBe(false);
    });
  });

  describe('isSubrecordAdded()', function(){
    it('should be true if all fields for the subrecord have been added', function(){
      var someSubrecord = {}
      var field1 = {
        name: "someField",
        subrecord: someSubrecord
      }

      var field2 = {
        name: "someOtherField",
        subrecord: someSubrecord
      }
      someSubrecord.fields = [
          field1, field2
      ];
      extractQuery.addSlice(field1);
      extractQuery.addSlice(field2);
      expect(extractQuery.isSubrecordAdded(someSubrecord)).toBe(true);
    });

    it('should be false if only some of the fields for the subrecord have been added', function(){
      var someSubrecord = {}
      var field1 = {
        name: "someField",
        subrecord: someSubrecord
      }

      var field2 = {
        name: "someOtherField",
        subrecord: someSubrecord
      }
      someSubrecord.fields = [
          field1, field2
      ];

      extractQuery.addSlice(field1);
      expect(extractQuery.isSubrecordAdded(someSubrecord)).toBe(false);
    });
  });

  describe('addSubrecordSlices()', function(){
    it('it should add all fields for the subrecord', function(){
      var someSubrecord = {}
      var field1 = {
        name: "someField",
        subrecord: someSubrecord
      }

      var field2 = {
        name: "someOtherField",
        subrecord: someSubrecord
      }
      someSubrecord.fields = [
          field1, field2
      ];

      extractQuery.addSubrecordSlices(someSubrecord);
      var slices = _.pluck(extractQuery.slices, "name");
      expect(slices.indexOf("someField") !== -1).toBe(true);
      expect(slices.indexOf("someOtherField") !== -1).toBe(true);
    });
  });

  describe('removeSubrecordSlices', function(){
    it('it should remove all fields for the subrecord', function(){
      var someSubrecord = {}
      var field1 = {
        name: "someField",
        subrecord: someSubrecord
      }

      var field2 = {
        name: "someOtherField",
        subrecord: someSubrecord
      }
      someSubrecord.fields = [
          field1, field2
      ];
      extractQuery.addSubrecordSlices(someSubrecord);
      extractQuery.removeSubrecordSlices(someSubrecord);
      var slices = _.pluck(extractQuery.slices, "name");
      expect(slices.indexOf("someField") === -1).toBe(true);
      expect(slices.indexOf("someOtherField") === -1).toBe(true);
    });
  });

  describe('removeSlice()', function(){
    it('should add a field to the slice', function(){
      extractQuery.slices.push("someField");
      extractQuery.removeSlice("someField");
      expect(extractQuery.slices.length).toBe(
        extractQuery.requiredExtractFields.length
      );
    });

    it('should not remove a required field', function(){
      extractQuery.removeSlice(extractQuery.requiredExtractFields[0]);
      expect(extractQuery.slices.length).toBe(
        extractQuery.requiredExtractFields.length
      );
    });
  });

  describe('getDataSlices()', function(){
    it('should handle the case where there are many slices', function(){
      extractQuery.slices = [
        {
          subrecord: {name: "episode"},
          name: "start"
        },
        {
          subrecord: {name: "episode"},
          name: "end"
        },
        {
          subrecord: {name: "diagnosis"},
          name: "condition"
        }
      ];
      var result = extractQuery.getDataSlices();
      var expected = {
        episode: ["start", "end"],
        diagnosis: ["condition"]
      };

      expect(result).toEqual(expected);
    });
  });

  describe('Getting Complete Criteria', function(){
    it('should be true if we have a query', function(){
        extractQuery.criteria[0].column = 'demographics';
        extractQuery.criteria[0].field = 'surname';
        extractQuery.criteria[0].queryType = 'contains';
        extractQuery.criteria[0].query = 'jane';
        expect(extractQuery.completeCriteria().length).toBe(1);
    });

    it('should be false if we have no query', function(){
        extractQuery.criteria[0].column = 'demographics';
        extractQuery.criteria[0].field = 'name';
        extractQuery.criteria[0].queryType = 'contains';
        expect(extractQuery.completeCriteria().length).toBe(0);
    });

    it("should update the critieria to or if we're of anyOrAll is 'any'", function(){
      extractQuery.anyOrAll = "any";
      extractQuery.criteria[0].column = 'demographics';
      extractQuery.criteria[0].field = 'surname';
      extractQuery.criteria[0].queryType = 'contains';
      extractQuery.criteria[0].query = 'jane';
      var result = extractQuery.completeCriteria();
      expect(result[0].combine).toBe('or');
    });

    it("should update the critieria to and if we're of anyOrAll is 'all'", function(){
      extractQuery.anyOrAll = "all";
      extractQuery.criteria[0].column = 'demographics';
      extractQuery.criteria[0].field = 'surname';
      extractQuery.criteria[0].queryType = 'contains';
      extractQuery.criteria[0].query = 'jane';
      var result = extractQuery.completeCriteria();
      expect(result[0].combine).toBe('and');
    });
  });

  describe('addFilter()', function(){
    it('should add a criteria', function(){
        expect(extractQuery.criteria.length).toBe(1);
        extractQuery.addFilter();
        expect(extractQuery.criteria.length).toBe(2);
    });
  });


  describe('readableQueryType()', function(){
    it('should return null if its handed a null', function(){
      // we hand the function null if we're looking at tagging
      expect(extractQuery.readableQueryType(null)).toBe(null);
    });

    it('should lower case the result', function(){
      expect(extractQuery.readableQueryType('Contains')).toBe('contains');
    });

    it('should add "is" as a prefix for time queries', function(){
      expect(extractQuery.readableQueryType('Before')).toBe('is before');
      expect(extractQuery.readableQueryType('After')).toBe('is after');
    });

    it('should change equals to "is"', function(){
      expect(extractQuery.readableQueryType('Equals')).toBe('is');
    });

    it('should change All Of to "is"', function(){
      expect(extractQuery.readableQueryType('All Of')).toBe('is');
    });

    it('should change Any Of to "is"', function(){
      expect(extractQuery.readableQueryType('Any Of')).toBe('is');
    });
  });

  describe('removeFilter()', function(){
    it('should always leave an empty filter', function(){
        expect(extractQuery.criteria.length).toBe(1);
        extractQuery.removeFilter();
        expect(extractQuery.criteria.length).toBe(1);
        expect(extractQuery.criteria[0].column).toBe(null);
    });

    it('should remove a criteria', function(){
        extractQuery.addFilter();
        expect(extractQuery.criteria.length).toBe(2);
        extractQuery.removeFilter();
        expect(extractQuery.criteria.length).toBe(1);
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
        extractQuery.resetFilter(criteria, ['column']);
        expect(criteria.column).toEqual("demographics");
        expect(criteria.field).toEqual(null);
        expect(criteria.query).toEqual(null);
        expect(criteria.queryType).toEqual(null);
    });

    it('should reset the field', function(){
        extractQuery.resetFilter(criteria, ['column', 'field']);
        expect(criteria.column).toEqual("demographics");
        expect(criteria.field).toEqual("name");
        expect(criteria.query).toEqual(null);
        expect(criteria.queryType).toEqual(null);
    });
  });

  describe('removeCriteria', function(){
      it('should reset the criteria', function(){
          extractQuery.criteria.push('hello world');
          extractQuery.removeCriteria();
          expect(extractQuery.criteria.length).toBe(1);
      });
  });
});
