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

	$scope.mouseRix = -1; // index of row mouse is currently over
	$scope.mouseCix = -1; // index of column mouse is currently over

	$http.get('data/records.json').success(function(rows) {
		for (var rix = 0; rix < rows.length; rix++) {
			for (var cix = 0; cix < $scope.columns.length; cix++) {
				if ($scope.columns[cix].multi) {
					rows[rix][$scope.columns[cix].name].push({});
				}
			}
		}
		$scope.rows = rows;
	});

	$scope.columns = [
		{name: 'location', title: 'Location', multi: false},
		{name: 'demographics', title: 'Demographics', multi: false}, 
		{name: 'diagnosis', title: 'Diagnosis', multi: true},
		{name: 'pastMedicalHistory', title: 'Past Medical History', multi: true},
		{name: 'generalNotes', title: 'Notes', multi: true},
		{name: 'travel', title: 'Travel', multi: true},
		//	{name: 'microbiology', title: '', multi: true}, TODO: awaiting details of structure
		{name: 'antimicrobials', title: 'Antimicrobials', multi: true},
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

	$http.get('data/antimicrobials.json').success(function(antimicrobials) {
		$scope.antimicrobials = antimicrobials;
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
			$scope.rows[rix][columnName][iix] = clone($scope.editing);
			if (iix + 1 == getNumItems(rix, cix)) {
				$scope.rows[rix][columnName].push({});
			}
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

	$scope.selectItem = function(rix, cix, iix) {
		$scope.rix = rix;
		$scope.cix = cix;
		$scope.iix = iix;
	}

	$scope.editItem = function(rix, cix, iix) {
		$scope.selectItem(rix, cix, iix);
		startEdit();
	}

	$scope.mouseEnter = function(rix, columnName) {
		$scope.mouseRix = rix;
		$scope.mouseCix = $scope.getCix(columnName);
	}

	$scope.mouseLeave = function() {
		$scope.mouseRix = -1;
		$scope.mouseCix = -1;
	}

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
			var contents;

			if (tAttrs.single == 'yes') {
				iterable = '[' + iterable + ']';
				contents = '<fielditem column="' + column + '"/>';
			} else {
				contents = '' +
				     '<span ng-hide="$last">' +
				       '<fielditem column="' + column + '"/>' +
				     '</span>' +
				     '<span ng-show="$last">' +
				       '<span ng-show="($parent.$index == rix && ' + // $parent.$index is the row index
						       'getCix(\'' + column + '\') == cix) ||' +
						      '($parent.$index == mouseRix && ' +
						       'getCix(\'' + column + '\') == mouseCix)">' +
					 'Add' +
				       '</span>&nbsp;' + // the nbsp is so that row heights don't change when Add is visible
				     '</span>'
			}

			return '' + 
			  '<ul>' +
			    '<li ng-repeat="item in ' + iterable + '"' + 
			        'ng-click="selectItem($parent.$index,' + // $parent.$index is the row index
				                     'getCix(\'' + column + '\'),' +
						     '$index)"' + // $index is the item index
			        'ng-dblclick="editItem($parent.$index,' +
				                      'getCix(\'' + column + '\'),' +
						      '$index)"' +
			        'ng-class="{selected: $parent.$index == rix && ' + 
				                     'getCix(\'' + column + '\') == cix && ' +
						     '$index == iix}">' +
			       contents +
			   '</li>' +
			 '</ul>';
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

app.directive('modal', function() {
	return {
		restrict: 'E',
		template: function(tElement, tAttrs) {
			var column = tAttrs.column;
			return '' +
			  '<div id="' + column + '-modal" class="modal hide" tabindex="-1" role="dialog">' +
			    '<div class="modal-header">' +
			      '<button type="button" class="close" data-dismiss="modal" ng-click="cancelEdit()">×</button>' +
			      '<h3>{{columns[getCix("' + column + '")].title}}</h3>' +
			    '</div>' +
			    '<div class="modal-body"><modalform column="' + column + '" /></div>' +
			    '<div class="modal-footer">' +
			      '<button class="btn" data-dismiss="modal" ng-click="cancelEdit()">Cancel</button>' +
			      '<button class="btn btn-primary" data-dismiss="modal" ng-click="saveEdit()">Save changes</button>' +
			    '</div>' +
			  '</div>'

		},
	}
});

app.directive('modalform', function() {
	return {
		restrict: 'E',
		templateUrl: function(tElement, tAttrs) {
			return 'templates/' + tAttrs.column + '-modal.html'
		},
	}
});
