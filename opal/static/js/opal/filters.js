var filters = angular.module('opal.filters', []);

filters.filter('microresult', function() {
	return function(input) {
		if (input == 'positive') {
			return 'POS';
		} else if (input == 'negative') {
			return 'NEG';
		} else if (input == 'equivocal') {
			return 'EQUIV';
		} else {
			return input;
		};
	};
});

filters.filter('boxed',  function(){
    return function(input){
        if(input == true){
            return '[X]'
        }
        return '[ ]'
    }
})

filters.filter('shortDate', function(){
    return function(input){
        if(!input){
            return
        }
        var d = moment(input)
        if (d.year() <= 2000) {
            // if the date was before 1/1/2001,
            // show the full year
            return d.format('DD/MM/YYYY')
        }
        else if (d.year() == moment().year()) {
            // if the date was this year,
            // don't show the year
            return d.format('DD/MM')
        }
        // show the year as two digits
        return d.format('DD/MM/YY')
    }
})

filters.filter('hhmm', function(){
    return function(input, change){
        if(!input){
            return;
        }
        var value = moment(input)
        return value.hours() + ':' + value.minutes();
    }
});

filters.filter('daysSince', function(){
    return function(input, change){
        if(!input){
            return;
        }
        diff = moment().diff(moment(input), 'days')
        if(change){
            return diff + change
        }
        return diff
    }
})

filters.filter('hoursSince', function(){
    return function(input){
        if(!input){
            return null;
        }
        t = input.toString()
        target = moment()
        target.hour(t.substr(0, 2))
        target.minutes(t.substr(2))
        diff =  moment().diff(target, 'hours')
        return diff
    }
});

filters.filter('future', function(){
    return function(input){
        var today = new Date();
        return input >= today;
    }
});

filters.filter('age', function(){
    return function(input){
        if(!input){
            return null;
        }
        target = moment(input)
        diff =  moment().diff(target, 'years')
        return diff        
    }
});

filters.filter('upper', function(){
    return function(input){
        if(!input){ return null };
        return input.toUpperCase();
    }
});

filters.filter('totalDays', function(){
    return function(item){
        if(!item.start_date){ return null };
        var start = moment(item.start_date);
        if(item.end_date){
            return moment(item.end_date).diff(start, 'days') + 1;
        }else{
            return moment().diff(start, 'days') + 1;
        }
    }    
});

filters.filter('daysTo', function(){
    return function(frist, second){
        var start = moment(frist);
        return moment(second).diff(start, 'days');
    }    
})
