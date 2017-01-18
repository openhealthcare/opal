describe('filters', function() {
    "use strict";

    beforeEach(module('opal.filters'));

    describe('microresultFilter', function(){
        var microresult;

        beforeEach(function(){
            inject(function($injector){
                microresult  = $injector.get('microresultFilter');
            });
        });

        it('should return pos', function(){
            expect(microresult('positive')).toEqual('POS');
        });

        it('should return neg', function(){
            expect(microresult('negative')).toEqual('NEG');
        });

        it('should return equiv', function(){
            expect(microresult('equivocal')).toEqual('EQUIV');
        });

        it('should do nothing', function(){
            expect(microresult('wat')).toEqual('wat');
        });

    })

    describe('boxed', function(){
        var boxed

        beforeEach(function(){
            inject(function($injector){
                boxed  = $injector.get('boxedFilter');
            });
        });

        it('should be boxed done', function(){
            expect(boxed(true)).toEqual('[X]');
        });

        it('should be boxed todo', function(){
            expect(boxed(false)).toEqual('[ ]');
        });

    });

    describe('plural', function(){
        var plural;

        beforeEach(function(){
            inject(function($injector){
                plural  = $injector.get('pluralFilter');
            });
        });

        it('should be many', function(){
            expect(plural('box', 2, 'boxes')).toEqual('boxes');
        });

        it('should be singular', function(){
            expect(plural('box', 1, 'boxes')).toEqual('box');
        });

        it('should use the default', function(){
            expect(plural('ball', 3)).toEqual('balls');
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

    describe('shortDate', function() {

        it('should return undefined for no input',
           inject(function(shortDateFilter) {
               expect(shortDateFilter(null)).toBe(undefined);
           }));

        it('should output a date before 1/1/2001 as DD/MM/YYYY',
           inject(function(shortDateFilter) {
               expect(shortDateFilter(new Date(2000, 1, 1))).toBe('01/02/2000');
           }));

        it('should output a date before this year as DD/MM/YY',
           inject(function(shortDateFilter) {
               expect(shortDateFilter(new Date(2001, 1, 1))).toBe('01/02/01');
           }));

        it('should output a date this year as DD/MM',
           inject(function(shortDateFilter) {
               expect(shortDateFilter(new Date(new Date().getFullYear(), 1, 1))).toBe('01/02');
           }));
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

    describe('shortDateTime', function(){
        var shortDateTime;

        beforeEach(function(){
            inject(function($injector){
                shortDateTime = $injector.get('shortDateTimeFilter');

            });
        });

        it('should return undefined if no input', function(){
            expect(shortDateTime(null)).toBe(undefined);
        });
        it('correct represent a string in date time format', function(){
            var expected = shortDateTime(new Date(2000, 1, 1, 20, 45));
            expect(expected).toBe('01/02/2000 20:45');
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
                futureFilter = $injector.get('futureFilter')

            });
            today = new Date();
        });

        it('should return true if in the future', function(){
            var tomorrow = today.setDate(today.getDate()+10);
            expect(futureFilter(tomorrow)).toBe(true);
        });

        it('should return true if today', function(){
            expect(futureFilter(new Date())).toBe(true);
        });

        it('should return fals if in the past', function(){
            var yesterday = today.setDate(today.getDate()-10);
            expect(futureFilter(yesterday)).toBe(false);
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
