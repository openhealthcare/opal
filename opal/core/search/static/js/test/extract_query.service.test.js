describe('ExtractQuery', function(){
  "use strict";

  var ExtractQuery, extractQuery;
  beforeEach(function(){
    module('opal.services');
    inject(function($injector){
      ExtractQuery = $injector.get('ExtractQuery');
    });
    extractQuery = new ExtractQuery('all')
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
      extractQuery.completeCriteria();
      expect(extractQuery.criteria[0].combine).toBe('or');
    });

    it("should update the critieria to and if we're of anyOrAll is 'all'", function(){
      extractQuery.anyOrAll = "all";
      extractQuery.completeCriteria();
      expect(extractQuery.criteria[0].combine).toBe('and');
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
