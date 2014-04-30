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

filters.filter('daysSince', function(){
    return function(input, change){
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
})
