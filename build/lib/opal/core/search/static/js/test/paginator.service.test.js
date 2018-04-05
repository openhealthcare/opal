describe('paginator', function(){
  "use strict";

  var Paginator;
  var spy;

  beforeEach(function(){
      module('opal.services');

      inject(function($injector) {
          Paginator = $injector.get('Paginator');
      });

      spy = jasmine.createSpy('spy');
  });

  it('should handle cases where there is only one page', function () {
      var args = {
        page_number: 1,
        total_count: 7,
        total_pages: 1
      };

      var paginator = new Paginator(spy, args);

      expect(paginator.hasNext).toBeFalsy();
      expect(paginator.hasPrevious).toBeFalsy();
      expect(paginator.totalPages).toEqual([1]);
      expect(spy.calls.all()).toEqual([]);
  });

  it('should handle cases where there is only two pages', function () {
      var args = {
        page_number: 1,
        total_count: 12,
        total_pages: 2
      };

      var paginator = new Paginator(spy, args);

      // hasNext means if there are more than numberOfPageResultsDisplayed pages
      expect(paginator.hasNext).toBeFalsy();
      expect(paginator.hasPrevious).toBeFalsy();
      expect(paginator.totalPages).toEqual([1, 2]);
      paginator.goNext();
      expect(spy.calls.first().args).toEqual([2]);
  });

  it("should handle the case when we're at the beginning of 11 pages", function(){
      var args = {
        page_number: 2,
        total_count: 101,
        total_pages: 11
      };

      var paginator = new Paginator(spy, args);
      expect(paginator.hasNext).toBeTruthy();
      expect(paginator.hasPrevious).toBeFalsy();
      expect(paginator.totalPages).toEqual([1, 2, 3, 4, 5, 6, 7]);
      paginator.goNext();
      expect(spy.calls.first().args).toEqual([3]);
  });


  it("should handle the case when we're in the middle of 15 pages", function(){
      var args = {
        page_number: 8,
        total_count: 141,
        total_pages: 15
      };

      var paginator = new Paginator(spy, args);
      expect(paginator.hasNext).toBeTruthy();
      expect(paginator.hasPrevious).toBeTruthy();
      expect(paginator.totalPages).toEqual([8, 9, 10, 11, 12, 13, 14]);
      paginator.goPrevious();
      expect(spy.calls.first().args).toEqual([7]);
  });

  it("should handle the when we're in the last of 15 pages", function(){
    var args = {
      page_number: 15,
      total_count: 141,
      total_pages: 15
    };

    var paginator = new Paginator(spy, args);
    expect(paginator.hasNext).toBeFalsy();
    expect(paginator.hasPrevious).toBeTruthy();
    expect(paginator.totalPages).toEqual([9, 10, 11, 12, 13, 14, 15]);
    paginator.goPrevious();
    expect(spy.calls.first().args).toEqual([14]);
  });
});
