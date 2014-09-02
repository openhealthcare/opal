describe('filters', function() {

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

        it('should return true if toady', function(){
            expect(futureFilter(today)).toBe(true);
        });

        it('should return fals if in the past', function(){
            var yesterday = today.setDate(today.getDate()-10);
            expect(futureFilter(yesterday)).toBe(false);
            
        });
    });

});
