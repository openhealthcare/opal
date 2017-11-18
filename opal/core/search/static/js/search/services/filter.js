angular.module('opal.services')
    .factory('Filter', function($http, $q, $window) {
    return function(resource){
        var filter = this;

        this.initialise = function(attrs){
            angular.extend(filter, attrs);
        }

        this.save = function(attrs){
            var url = '/search/filters/';
            var deferred = $q.defer();
            var method;

	        if (angular.isDefined(filter.id)) {
		        method = 'put';
		        url += attrs.id + '/';
	        } else {
		        method = 'post';
	        }


            $http[method](url, attrs).then(
                function(response){
                    filter.initialise(response.data);
                    deferred.resolve(filter);
                },
                function(response) {
		            // TODO handle error better
		            if (response.status == 409) {
			            $window.alert('Item could not be saved because somebody else has \
recently changed it - refresh the page and try again');
		            } else {
			            $window.alert('Item could not be saved');
		            };
                    deferred.reject()
		        }
            );
            return deferred.promise;
        };

        this.destroy = function(){
	        var deferred = $q.defer();
	        var url = '/search/filters/' + this.id + '/';

	        $http['delete'](url).then(function(response) {
		        deferred.resolve();
	        }, function(response) {
		        // handle error better
		        $window.alert('Item could not be deleted');
	        });
	        return deferred.promise;

        }

        this.initialise(resource);
    };
});
