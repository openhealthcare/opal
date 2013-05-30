var columns = [
	{name: 'location', multi: false},
	{name: 'demographics', multi: false}, 
	{name: 'diagnosis', multi: true},
	{name: 'pastMedicalHistory', multi: true},
	{name: 'travel', multi: true},
//	{name: 'microbiology', multi: true}, TODO: awaiting details of structure
	{name: 'antibiotics', multi: true},
	{name: 'microbiologyComments', multi: true},
	{name: 'plan', multi: false},
	{name: 'discharge', multi: false},
];

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

	var rix = 0;
	var cix = -1;
	var iix = -1;
	var editing = false;

	$http.get('data/records.json').success(function(rows) {
		for (var rix = 0; rix < rows.length; rix++) {
			for (var cix = 0; cix < columns.length; cix++) {
				if (columns[cix].multi) {
					rows[rix][columns[cix]['name']].push({'_new': true});
				}
			}
		}
		$scope.rows = rows;
		selectRow();
	});

	function selectRow() {
		$scope.rows[rix]['_selected'] = true;
	};

	function deselectRow() {
		delete $scope.rows[rix]['_selected'];
	};

	function selectColumn() {
		$scope.selectedColumnName = columns[cix]['name'];
		if (columns[cix]['multi']) {
			iix = 0;
			selectItem();
		} else {
			iix = -1;
		}
	};

	function deselectColumn(cir) {
		$scope.selectedColumnName = null;
	};

	function selectItem() {
		$scope.rows[rix][$scope.selectedColumnName][iix]['_selected'] = true;
	};

	function deselectItem() {
		delete $scope.rows[rix][$scope.selectedColumnName][iix]['_selected'];
	};

	function doEdit() {
		editing = true;
		if (columns[cix]['multi']) {
			$scope.editing = clone($scope.rows[rix][$scope.selectedColumnName][iix]);
		} else {
			$scope.editing = clone($scope.rows[rix][$scope.selectedColumnName]);
		}
		$('#' + $scope.selectedColumnName + '-modal').modal()
		$('#' + $scope.selectedColumnName + '-modal').find('input').first().focus();
	};

	$scope.saveEdit = function() {
		editing = false;
		if (columns[cix]['multi']) {
			if ($scope.editing._new) {
				delete $scope.editing._new;
				$scope.rows[rix][$scope.selectedColumnName].push({'_new': true});
			}

			$scope.rows[rix][$scope.selectedColumnName][iix] = clone($scope.editing);
		} else {
			$scope.rows[rix][$scope.selectedColumnName] = clone($scope.editing);
		}
	};

	$scope.cancelEdit = function() {
		editing = false;
	};

	$scope.keypress = function(e) {
		if (editing) {
			return;
		}
		if (cix == -1) {
			switch (e.keyCode) {
				case 38: // up
				case 75: // k
					if (rix > 0) {
						deselectRow();
						rix--;
						selectRow();
					}
					break;
				case 40: // down
				case 74: // j
					if (rix < $scope.rows.length-1) {
						deselectRow();
						rix++;
						selectRow();
					}
					break;
				case 32: // space
					cix = 0;
					selectColumn();
					break;
			}
		} else {
			switch (e.keyCode) {
				case 37: // left
				case 72: // h
					if (cix > 0) {
						deselectColumn();
						cix--;
						selectColumn();
					}
					break;
				case 39: // right
				case 76: // l
					if (cix < columns.length-1) {
						deselectColumn();
						cix++;
						selectColumn();
					}
				break;
				case 38: // up
				case 75: // k
					if (iix > 0) {
						deselectItem();
						iix--;
						selectItem();
					}
					break;
				case 40: // down
				case 74: // j
					if (iix < $scope.rows[rix][$scope.selectedColumnName].length-1) {
						deselectItem();
						iix++;
						selectItem();
					}
					break;
				case 13: // return
					doEdit();
					break;
				case 32: // space
					deselectColumn();
					cix = -1;
					break;
			}
		}
	}
});
