var app = angular.module('opalApp', []);

app.controller('TableCtrl', function($scope, $http) {
	$scope.rows = [];

	var selectedRowIx = 0;

	$http.get('data/records.json').success(function(records) {
		$scope.records = records;

		for (var rix = 0; rix < records.length; rix++) {
			$scope.rows.push({_data: records[rix]});
		};

		selectRow(selectedRowIx);
	});

	function selectRow(rix) {
		$scope.rows[rix]['selected'] = true;
	};

	function deselectRow(rix) {
		delete $scope.rows[rix]['selected'];
	};

	$scope.keypress = function(e) {
		switch (e.keyCode) {
			case 38: // up
			case 75: // k
				if (selectedRowIx > 0) {
					deselectRow(selectedRowIx);
					selectedRowIx--;
					selectRow(selectedRowIx);
				}
				break;
			case 40: // down
			case 74: // j
				if (selectedRowIx < $scope.rows.length-1) {
					deselectRow(selectedRowIx);
					selectedRowIx++;
					selectRow(selectedRowIx);
				}
				break;
		};
	}
});
