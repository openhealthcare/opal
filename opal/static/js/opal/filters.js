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

filters.filter('plural', function(){
		return function(someWord, count, plural){
				if(count === 1){
					 return someWord;
				}
				else if(plural){
					 return plural;
				}
				return someWord + "s";
		};
});

filters.filter('toMoment', function(){
		return function(input){
				if(!input){
						return;
				}
				var d = moment(input);

				if(!d.isValid()){
						d = moment(input, 'DD/MM/YYYY');
				}

				return d;
		};
});

filters.filter('fromNow', function(toMomentFilter){
		return function(input){
				if(!input){
						return;
				}
				var momented = toMomentFilter(input);
				return momented.fromNow();
		};
});

filters.filter('shortDate', function(toMomentFilter){
    return function(input){
        if(!input){
            return
        }

				d = toMomentFilter(input);

        if (d.year() <= 2000) {
            // if the date was before 1/1/2001,
            // show the full year
            return d.format('DD/MM/YYYY');
        }
        else if (d.year() == moment().year()) {
            // if the date was this year,
            // don't show the year
            return d.format('DD/MM');
        }
        // show the year as two digits
        return d.format('DD/MM/YY');
    }
});

filters.filter('momentDateFormat', function(){
	return function(input, format){
			if(!input){
					return
			}
			var d = moment(input)
			return d.format(format)
	}
});

filters.filter('hhmm', function(){
    return function(input, change){
        if(!input){
            return;
        }
        var value = moment(input)
        return value.hours() + ':' + value.minutes();
    }
});


filters.filter('daysTo', function(){
    return function(first, second, withoutDays){
				if(!first || !second){
						return;
				}

        var start = moment(first);
				var diff = moment(second).diff(start, 'days');

				if(withoutDays){
						return diff;
				}
				else{
						// don't use moment.from as it abstracts to months
						// by rounding up/down
						if(diff === 1){
								return "1 day";
						}
						else{
								return diff + " days";
						}
				}
    };
});

filters.filter('daysSince', function(daysToFilter){
    return function(input, change, withoutDays){
        if(!input){
            return;
        }
				endDate = moment();

				if(change){
						endDate.add(change, "days");
				}
				return daysToFilter(input, endDate, withoutDays);
    };
});

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

filters.filter('title', function(){
	return function(s) {
        s = ( s === undefined || s === null ) ? '' : s;
        return s.toString().replace( /\b([a-zA-Z])/g, function(ch) {
            return ch.toUpperCase();
        });
    };
});

filters.filter('totalDays', function(){
    return function(item){
        if(!item.start_date){ return null; };
        var start = moment(item.start_date);

				if(!start.isValid()){
						start = moment(item.start_date, 'DD/MM/YYYY');
				}

        if(item.end_date){
						end = moment(item.end_date);
						if(!end.isValid()){
							end = moment(item.end_date, 'DD/MM/YYYY');
						}
            return end.diff(start, 'days') + 1;
        }else{
            return moment().diff(start, 'days') + 1;
        }
    }
});
