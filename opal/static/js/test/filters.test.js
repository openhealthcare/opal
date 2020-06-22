describe('filters', function() {
  "use strict";

  beforeEach(module('opal.filters'));

  describe('displayArray', function(){
    var displayArray;

    beforeEach(function(){
      inject(function($injector){
        displayArray  = $injector.get('displayArrayFilter');
      });
    });

    it('should return the original if its not an array', function(){
      expect(displayArray('onions')).toBe('onions');
    });

    it('should combine with and', function(){
      expect(displayArray(['onions', 'lettuce'])).toEqual(
        "onions and lettuce"
      );
    });

    it('should combine with or', function(){
      expect(displayArray(['onions', 'lettuce'], "or")).toEqual(
        "onions or lettuce"
      );
    });

    it('should add commas', function(){
      expect(displayArray(['onions', "tomatoes", 'lettuce'], "or")).toEqual(
        "onions, tomatoes or lettuce"
      );
    });

    it('should just return the result if the array is only a single element', function(){
      expect(displayArray(['onions'])).toEqual("onions");
    });
  });

  describe('toMoment', function(){
    var toMoment;

    beforeEach(function(){
      inject(function($injector){
        toMoment  = $injector.get('toMomentFilter');
      });
    });

    it('shoud be null if null', function(){
      expect(toMoment(null)).toBe(undefined);
    })

    it('should take DDMMYYYY', function(){
      var expected = new Date(1989, 11, 27);
      expect(toMoment('27/12/1989').toDate()).toEqual(expected);
    })

    it('should take datetimes', function() {
      var expected = new Date(1999, 3, 1, 4, 52);
      expect(toMoment('01/04/1999 04:52:00'));
    });
  });

  describe('fromNow()', function() {
    var fromNow;

    beforeEach(function(){
      inject(function($injector){
        fromNow  = $injector.get('fromNowFilter');
      });
    });

    it('should return nill if null', function() {
      expect(fromNow(null)).toBe(undefined);
    });

    it('should return the time fromNow', function() {
      var today = new Date(2002, 2, 22);
      jasmine.clock().mockDate(today);
      expect(fromNow('20/03/2002')).toEqual('2 days ago');
    });

  });

  describe('shortTime', function(){
    var shortTime;

    beforeEach(function(){
      inject(function($injector){
        shortTime  = $injector.get('shortTimeFilter');
      });

    });

    it('should display the time as hh:mm from string', function(){
      expect(shortTime('10:12:00')).toBe('10:12');
    });

    it('should display the time as hh:mm from date', function(){
      var weCare = new Date(2017, 10, 1, 10, 12);
      expect(shortTime(weCare)).toBe('10:12');
    });

    it('should display the time as hh:mm from moment', function(){
      var weCare = moment(new Date(2017, 10, 1, 10, 12));
      expect(shortTime(weCare)).toBe('10:12');
    });
  });

  describe('displayDate()', function() {
    var displayDate;
    var date_display_format = 'D MMM YYYY';

    beforeEach(function(){
      module(function($provide){
        $provide.value('DATE_DISPLAY_FORMAT', date_display_format);
      });

      inject(function($injector){
        displayDate = $injector.get('displayDateFilter');
      });
    });


    it('should format as D MMM YYYY', function() {
      var d = new Date(1959, 2, 3);
      expect(displayDate(d)).toBe('3 Mar 1959');
    });

    it('should return undefined if passed null', function() {
      expect(displayDate(null)).toEqual(undefined);
    });

  });

  describe('displayDateTime()', function() {
    var displayDateTime;
    var date_display_format = 'D MMM YYYY';

    beforeEach(function(){
      module(function($provide){
        $provide.value('DATE_DISPLAY_FORMAT', date_display_format);
      });

      inject(function($injector){
        displayDateTime = $injector.get('displayDateTimeFilter');
      });

    });

    it('should display the date time as D MMM YYYY h:s', function() {
      expect(displayDateTime(new Date(1959, 2, 3, 19, 12))).toBe(
        '3 Mar 1959 19:12'
      );
    });

    it('should return_nothing if null', function() {
      expect(displayDateTime(null)).toEqual(undefined);
    });

  });

  describe('momentDateFormat()', function() {
    var momentDateFormat;

    beforeEach(function(){
      inject(function($injector){
        momentDateFormat = $injector.get('momentDateFormatFilter');

      });
    });

    it('should return nothing if null', function() {
      expect(momentDateFormat(null)).toBe(undefined);
    });

    it('should return a formatted string', function() {
      var res = momentDateFormat(new Date(2000, 1, 1), "YYYY-MM-DD");
      expect(res).toEqual('2000-02-01');
    });

  });

  describe('hhmm', function() {
    var hhmm;

    beforeEach(function(){
      inject(function($injector){
        hhmm = $injector.get('hhmmFilter');

      });
    });

    it('should return undefined if not input', function() {
      expect(hhmm(null)).toBe(undefined);
    });

    it('should return the hours and minutes string', function() {
      expect(hhmm(new Date(201, 3, 12, 8, 45))).toEqual('8:45');
    });

  });

  describe('daysTo', function() {
    var daysTo

    beforeEach(function(){
      inject(function($injector){
        daysTo = $injector.get('daysToFilter');

      });
    });

    it('should return undefined if not first', function() {
      expect(daysTo(null, null, null)).toBe(undefined);
    });

    it('should return undefined if not second', function() {
      expect(daysTo(new Date(1999, 0, 12), null)).toBe(undefined);
    });

    it('should return the difference in days as a string', function() {
      expect(daysTo(new Date(1999, 0, 12), new Date(1999, 0, 14))).toBe('2 days')
    });

    it('should return the difference of a single day as a string', function() {
      expect(daysTo(new Date(1999, 0, 12), new Date(1999, 0, 13))).toBe('1 day')
    });

    it('should return just the number if Without Days', function() {
      expect(daysTo(new Date(1999, 0, 12), new Date(1999, 0, 14), true)).toBe(2)
    });

  });

  describe('daysSince', function() {
    var daysSince

    beforeEach(function(){
      inject(function($injector){
        daysSince = $injector.get('daysSinceFilter');

      });
    });

    it('should return undefined if not first', function() {
      expect(daysSince(null)).toBe(undefined);
    });

    it('should return the number of days', function() {
      var today = new Date(2002, 2, 29);
      jasmine.clock().mockDate(today);

      expect(daysSince(new Date(2002, 1, 12), 3, true)).toEqual(48)
    });

  });

  describe('future', function(){
    var futureFilter, today;

    beforeEach(function(){
      inject(function($injector){
        futureFilter = $injector.get('futureFilter');

      });
      today = moment();
    });

    it('should return false if undefined', function(){
      expect(futureFilter(undefined)).toBe(false);
    })

    it('should return true if in the future', function(){
      var tomorrow = today.add(1, "days");
      expect(futureFilter(tomorrow)).toBe(true);
    });

    it('should return true if today if we include today', function(){
      expect(futureFilter(new Date(), true)).toBe(true);
    });

    it('should return true if today if we include today', function(){
      expect(futureFilter(new Date())).toBe(false);
    });

    it('should return fals if in the past', function(){
      var yesterday = today.subtract(1, "days");
      expect(futureFilter(yesterday)).toBe(false);
    });
  });

  describe('past', function(){
    var pastFilter, today;

    beforeEach(function(){
      inject(function($injector){
        pastFilter = $injector.get('pastFilter');

      });
      today = moment();
    });

    it('should return false if undefined', function(){
      expect(pastFilter(undefined)).toBe(false);
    })

    it('should return true if in the future and passed a moment', function(){
      var tomorrow = today.add(1, "days");
      expect(pastFilter(tomorrow)).toBe(false);
    });

    it('should return false if in the future', function(){
      var tomorrow =  today.add(1, "days");
      expect(pastFilter(tomorrow)).toBe(false);
    });

    it('should return true if today if we include today', function(){
      expect(pastFilter(new Date(), true)).toBe(true);
    });


    it('should return true if today if we include today', function(){
      expect(pastFilter(new Date())).toBe(false);
    });

    it('should return true if in the past', function(){
      var yesterday = today.subtract(1, "days");
      expect(pastFilter(yesterday)).toBe(true);
    });

    it('should return true if in the past and passed a moment', function(){
      var yesterday = today.subtract(1, "days");
      expect(pastFilter(yesterday)).toBe(true);
    });
  });

  describe('age', function(){
    var ageFilter, today;

    beforeEach(function(){
      inject(function($injector){
        ageFilter = $injector.get('ageFilter')

      });
    });

    it('should be null if null', function(){
      expect(ageFilter(null)).toBe(null);
    })

    it('Should return the age in years', function () {
      var today = new Date(2016, 2, 22);
      jasmine.clock().mockDate(today);
      expect(ageFilter(new Date())).toBe(0);
      expect(ageFilter(new Date(2000,1,1))).toBe(16);
    });

  });


  describe('upper', function(){
    var upperFilter, today;

    beforeEach(function(){
      inject(function($injector){
        upperFilter = $injector.get('upperFilter')
      });
    });

    it('Should uppercase the input', function () {
      expect(upperFilter('this')).toBe('THIS');
    });

    it('should return null if input is not set', function(){
      expect(upperFilter(undefined)).toBe(null);
    });
  });

  describe('title', function(){
    var title;

    beforeEach(function(){
      inject(function($injector){
        title = $injector.get('titleFilter')
      });
    });

    it('Should return the titel', function () {
      expect(title('hello world')).toBe('Hello World');
    });

  });


  describe('underscoreToSpaces', function(){
    var underscoreToSpaces;

    beforeEach(function(){
      inject(function($injector){
        underscoreToSpaces = $injector.get('underscoreToSpacesFilter');
      });
    });

    it('Should return the change underscores to spaces', function () {
      expect(underscoreToSpaces('hello_world')).toBe('hello world');
    });

    it('Should handle nulls', function () {
      expect(underscoreToSpaces(null)).toBe('');
      expect(underscoreToSpaces(undefined)).toBe('');
    });
  });


  describe('totalDays', function(){
    var totalDaysFilter, today;

    beforeEach(function(){
      inject(function($injector){
        totalDaysFilter = $injector.get('totalDaysFilter')
      });
    });

    it('Should be null if no start date', function () {
      expect(totalDaysFilter({})).toBe(null)
    });

    it('Should return the diff in days', function () {
      var obj = {start_date: new Date(2000, 1, 1), end_date: new Date(2000, 1, 4)}
      expect(totalDaysFilter(obj)).toBe(4)
    });

    it('should return the diff to today if no end date', function() {
      var today = new Date(2000, 1, 22);
      jasmine.clock().mockDate(today);
      var obj = {start_date: new Date(2000, 1, 1)};
      expect(totalDaysFilter(obj)).toBe(22);
    });

  });

});
