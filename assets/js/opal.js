function clone(obj) {
	if (typeof obj == 'object') {
		return $.extend(true, {}, obj);
	} else {
		return obj;
	}
};

function getKeys(obj) {
    var keys = [];
    for (var key in obj) {
        if (obj.hasOwnProperty(key)) {
                    keys.push(key);
        }
    }
    return keys;
}

var app = angular.module('opalApp', ['$strap.directives']);

app.controller('TableCtrl', function($scope, $http) {
	var editing;

	$scope.rows = [];

	$scope.rix = 0; // row index
	$scope.cix = 0; // column index
	$scope.iix = 0; // item index

	$http.get('data/records.json').success(function(rows) {
//		for (var rix = 0; rix < rows.length; rix++) {
//			for (var cix = 0; cix < columns.length; cix++) {
//				if (columns[cix].multi) {
//					rows[rix][columns[cix]['name']].push({'_new': true});
//				}
//			}
//		}
		$scope.rows = rows;
	});

	$scope.columns = [
		{name: 'location', title: 'Location', multi: false},
		{name: 'demographics', title: 'Demographics', multi: false}, 
		{name: 'diagnosis', title: 'Diagnosis', multi: true},
		{name: 'pastMedicalHistory', title: 'Past Medical History', multi: true},
		{name: 'travel', title: 'Travel', multi: true},
		//	{name: 'microbiology', title: '', multi: true}, TODO: awaiting details of structure
		{name: 'antibiotics', title: 'Antibiotics', multi: true},
		{name: 'microbiologyComments', title: 'Microbiology Comments', multi: true},
		{name: 'plan', title: 'Plan', multi: false},
		{name: 'discharge', title: 'Discharge', multi: false},
	];

	$scope.getCix = function(name) {
		for (var cix = 0; cix < $scope.columns.length; cix++) {
			if ($scope.columns[cix].name == name) {
				return cix;
			}
		}
		throw 'Unexpected column name: ' + name
	};

	$http.get('data/conditions.json').success(function(conditions) {
		$scope.conditions = conditions;
	});

	$http.get('data/countries.json').success(function(countries) {
		$scope.destinations = countries;
	});

	$http.get('data/antibiotics.json').success(function(antibiotics) {
		$scope.antibiotics = antibiotics;
	});

	$scope.categories = ['Inpatient', 'Review', 'Followup'];
	$scope.routes = ['Oral', 'IV'];
	$scope.travelReasones = ['Visiting Friends and Relatives', 'Business', 'Military', 'Holiday'];

	function startEdit() {
		var rix = $scope.rix;
		var cix = $scope.cix;
		var iix = $scope.iix;
		var columnName = $scope.columns[cix].name;

		editing = true;
		if ($scope.columns[cix]['multi']) {
			$scope.editing = clone($scope.rows[rix][columnName][iix]);
		} else {
			$scope.editing = clone($scope.rows[rix][columnName]);
		}
		$('#' + columnName + '-modal').modal()
		$('#' + columnName + '-modal').find('input').first().focus();
	};

	$scope.saveEdit = function() {
		var rix = $scope.rix;
		var cix = $scope.cix;
		var iix = $scope.iix;
		var columnName = $scope.columns[cix].name;

		$('#' + columnName + '-modal').modal('hide')
		editing = false;
		if ($scope.columns[cix]['multi']) {
			if ($scope.editing._new) {
				delete $scope.editing._new;
				$scope.rows[rix][columnName].push({'_new': true});
			}

			$scope.rows[rix][columnName][iix] = clone($scope.editing);
		} else {
			$scope.rows[rix][columnName] = clone($scope.editing);
		}
	};

	$scope.cancelEdit = function() {
		var cix = $scope.cix;
		var columnName = $scope.columns[cix].name;

		$('#' + columnName + '-modal').modal('hide')
		editing = false;
	};

	function getNumItems(rix, cix) {
		var column = $scope.columns[cix];
		if (column.multi) {
			return $scope.rows[rix][column.name].length;
		} else {
			return 1;
		}
	};

	$scope.keypress = function(e) {
		if (editing) {
			switch (e.keyCode) {
				case 27: // escape
					$scope.cancelEdit();
					break;
			}
		} else {
			switch (e.keyCode) {
				case 37: // left
				case 72: // h
					goLeft();
					break;
				case 39: // right
				case 76: // l
					goRight();
					break;
				case 38: // up
				case 75: // k
					goUp();
					break;
				case 40: // down
				case 74: // j
					goDown();
					break;
				case 13: // enter
					startEdit();
					break;
			}
		}
	}

	function goLeft() {
		if ($scope.cix > 0) {
			$scope.cix--;
			$scope.iix = 0;
		}
	}

	function goRight() {
		if ($scope.cix < $scope.columns.length - 1) {
			$scope.cix++;
			$scope.iix = 0;
		}
	}

	function goUp() {
		if ($scope.iix > 0) {
			$scope.iix--;
		} else {
			if ($scope.rix > 0) {
				$scope.rix--;
				$scope.iix = getNumItems($scope.rix, $scope.cix) - 1;
			}
		}
	}

	function goDown() {
		if ($scope.iix < getNumItems($scope.rix, $scope.cix) - 1) {
			$scope.iix++;
		} else {
			if ($scope.rix < $scope.rows.length - 1) {
				$scope.rix++;
				$scope.iix = 0;
			}
		}
	}
});

app.directive('field', function() {
	return {
		restrict: 'E',
		template: function(tElement, tAttrs) {
			var column = tAttrs.column;
			var iterable = 'row.' + column;

			if (tAttrs.single == 'yes') {
				iterable = '[' + iterable + ']';
			}

			// $parent.$index is the row index
			// $index is the item index
			return '<ul><li ng-repeat="item in ' + iterable + '" ng-class="{selected: $parent.$index == rix && getCix(\'' + column + '\') == cix && $index == iix}"><fielditem column="' + column + '"/></li></ul>';
		},
	}
});

app.directive('fielditem', function() {
	return {
		restrict: 'E',
		templateUrl: function(tElement, tAttrs) {
			return 'templates/' + tAttrs.column + '.html'
		},
	}
});


