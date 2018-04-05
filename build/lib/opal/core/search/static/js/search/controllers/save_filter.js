angular.module('opal.controllers')
    .controller('SaveFilterCtrl', function($scope, $modalInstance, ngProgressLite, Filter, params) {
        $scope.model = params;

	    $scope.save = function(result) {
            var filter = new Filter($scope.model);
            ngProgressLite.set(0);
            ngProgressLite.start();
		    filter.save($scope.model).then(
                function(result) {
                    ngProgressLite.done();
			        $modalInstance.close(result);
		        },
                function() {
                    ngProgressLite.done();
                }
            );
	    };


	    $scope.cancel = function() {
		    $modalInstance.close('cancel');
	    };

    })
