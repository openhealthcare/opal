var columns = ['location', 'demographics'];

function clone(obj) {
	if (typeof obj == 'object') {
		return $.extend(true, {}, obj);
	} else {
		return obj;
	}
};

var app = angular.module('opalApp', []);

app.controller('TableCtrl', function($scope, $http) {
	$scope.rows = [];
	$scope.selectedColumnName = null;

	var selectedRowIx = 0;
	var selectedColumnIx = -1;

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

	function selectColumn(cix) {
		$scope.selectedColumnName = columns[cix];
	};

	function deselectColumn(cir) {
		$scope.selectedColumnName = null;
	}

	function editRow(rix) {
		$scope.editing = clone($scope.rows[rix]._data[$scope.selectedColumnName]);
		$('#' + $scope.selectedColumnName + '-modal').modal()
	};

	$scope.saveEdit = function() {
		$scope.rows[selectedRowIx]._data[$scope.selectedColumnName] = clone($scope.editing);
	};

	$scope.keypress = function(e) {
		if (selectedColumnIx == -1) {
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
				case 32: // space
					selectedColumnIx = 0;
					selectColumn(selectedColumnIx);
					break;
			}
		} else {
			switch (e.keyCode) {
				case 37: // left
				case 72: // h
					if (selectedColumnIx > 0) {
						deselectColumn(selectedColumnIx);
						selectedColumnIx--;
						selectColumn(selectedColumnIx);
					}
					break;
				case 39: // right
				case 76: // l
					if (selectedColumnIx < columns.length-1) {
						deselectColumn(selectedColumnIx);
						selectedColumnIx++;
						selectColumn(selectedColumnIx);
					}
				break;
				case 13: // return
					editRow(selectedRowIx);
					break;
				case 32: // space
					deselectColumn(selectedColumnIx);
					selectedColumnIx = -1;
					break;
			}
		}
	}
});
