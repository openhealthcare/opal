describe('filters', function() {
    "use strict";

    beforeEach(module('opal.filters'));

    describe('shortDate', function() {
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

        it('Should return the age in years', function () {
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

    });

});
