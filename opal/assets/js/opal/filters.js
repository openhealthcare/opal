var filters = angular.module('opal.filters', []);

filters.filter('opalDate', function() {
	return function(input) {
		// Converts a date to format 'dd/MM'.
		//
		// We can't use angular's built in date formatter because that only handles Date objects
		// or strings of the form 'yyyy-mm-dd'.  At some point we should convert all dates to Date
		// objects in client code.
		//
		// This assumes that if called with a string, the string will be of form dd/mm/yyyy
		if (typeof(input) == 'string') {
			return parseInt(input.split('/')[0], 10) + '/' + parseInt(input.split('/')[1]);
		} else {
			return input;
		}
	}
});
