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

// See http://stackoverflow.com/questions/8302928/angularjs-with-django-conflicting-template-tags
app.config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('[[');
	$interpolateProvider.endSymbol(']]');
});

app.controller('TableCtrl', function($scope, $http) {
	var editing = false;
	var deleting = false;

	$scope.rows = [];

	$scope.rix = 0; // row index
	$scope.cix = 0; // column index
	$scope.iix = 0; // item index

	$scope.mouseRix = -1; // index of row mouse is currently over
	$scope.mouseCix = -1; // index of column mouse is currently over


	$http.get('schema/').success(function(data) {
		var option_lists = data.option_lists;
		var option_names = getKeys(option_lists);
		var option_name;

		$scope.columns = data.columns;

		$http.get('patient/').success(function(rows) {
			for (var rix = 0; rix < rows.length; rix++) {
				for (var cix = 0; cix < $scope.columns.length; cix++) {
					if (!$scope.columns[cix].single) {
						rows[rix][$scope.columns[cix].name].push({patient: rows[rix].id});
					}
				}
			}
			$scope.rows = rows;
		});

		$scope.microbiology_test_list = [];
		$scope.microbiology_test_lookup = {};

		for (var kix = 0; kix < option_names.length; kix++) {
			option_name = option_names[kix];
			$scope[option_name + '_list'] = [];
			$scope[option_name + '_synonyms'] = {};
			for (var j = 0; j < option_lists[option_name].length; j++) {
				$scope[option_name + '_list'].push(option_lists[option_name][j][0]);
				$scope[option_name + '_synonyms'][option_lists[option_name][j][0]] = option_lists[option_name][j][1];
				if (option_name.indexOf('micro_test') == 0) {
					$scope.microbiology_test_list.push(option_lists[option_name][j][0]);
					$scope.microbiology_test_lookup[option_lists[option_name][j][0]] = option_name;
				}
			};
		}

		$scope.microbiology_test_list.sort();
	})

	$scope.getCategory = function(testName) {
		if ($scope.microbiology_test_lookup !== undefined) {
			return $scope.microbiology_test_lookup[testName];
		}
	};

	$scope.getSynonymn = function(option, term) {
		var synonyms = $scope[option + '_synonyms'];
		if (synonyms !== undefined) {
			// The list of synonyms may not have loaded yet.
			// This would be a problem if we serve non-canonical
			// data and try an canonicalise before the synonyms are
			// loaded.  I think we shouldn't serve non-canonical
			// data but there might be a good reason to.
			return synonyms[term] || term;
		} else {
			return term;
		}
	};

	function startEdit() {
		var rix = $scope.rix;
		var cix = $scope.cix;
		var iix = $scope.iix;
		var columnName = $scope.columns[cix].name;

		editing = true;
		if ($scope.columns[cix]['single']) {
			$scope.editing = clone($scope.rows[rix][columnName]);
		} else {
			$scope.editing = clone($scope.rows[rix][columnName][iix]);
		}
		$('#' + columnName + '-modal').modal();
		$('#' + columnName + '-modal').find('input,textarea').first().focus();
	};

	$scope.startAdd = function() {
		editing = true;
		$scope.editing = {location: {}, demographics: {}};
		$('#add-new-modal').modal();
		$('#add-new-modal').find('input,textarea').first().focus();
	};

	function startDelete() {
		var rix = $scope.rix;
		var cix = $scope.cix;
		var iix = $scope.iix;
		var column = $scope.columns[cix];

		if (column.single) {
			return;
		}

		if ($scope.rows[rix][column.name].length == 1) {
			return;
		}

		deleting = true;
		$('#delete-confirmation').modal();
		$('#delete-confirmation').find('.btn-primary').focus();
	};

	function clearModal(columnName) {
		$('#' + columnName + '-modal').modal('hide')

		// See https://github.com/openhealthcare/opal/issues/28
		document.activeElement.blur();
	};

	$scope.addRecord = function() {
		var newRecord = {};
		var column;

		$http.post('patient/').success(function(patient) {
			newRecord.id = patient.id;
			for (var cix = 0; cix < $scope.columns.length; cix++) {
				column = $scope.columns[cix];
				if (column.single) {
					newRecord[column.name] = {patient: patient.id};
				} else {
					newRecord[column.name] = [{patient: patient.id}];
				}
			}

			$scope.rows.push(newRecord);
			$scope.selectItem($scope.rows.length - 1, 0, 0);
			startEdit();
		});
	};

	$scope.saveAdd = function() {
		clearModal('add-new');
		editing = false;
		$http.post('patient/', $scope.editing).success(function(patient) {
			for (var cix = 0; cix < $scope.columns.length; cix++) {
				column = $scope.columns[cix];
				if (!column.single) {
					patient[column.name] = [{patient: patient.id}];
				}
			}
			$scope.rows.push(patient);
			$scope.selectItem($scope.rows.length - 1, 0, 0);
		});
	};

	$scope.saveEdit = function() {
		var rix = $scope.rix;
		var cix = $scope.cix;
		var iix = $scope.iix;
		var columnName = $scope.columns[cix].name;
		var url;

		clearModal(columnName);
		editing = false;

		if ($scope.columns[cix]['single']) {
			$scope.rows[rix][columnName] = clone($scope.editing);
			url = 'patient/' + $scope.rows[rix].id + '/' + columnName + '/';
			$http.put(url, $scope.editing);
		} else {
			$scope.rows[rix][columnName][iix] = clone($scope.editing);
			if (typeof($scope.editing.id) == 'undefined') {
				url = 'patient/' + $scope.rows[rix].id + '/' + columnName + '/';
				$http.post(url, $scope.editing);
			} else {
				url = 'patient/' + $scope.rows[rix].id + '/' + columnName + '/' + $scope.editing.id + '/';
				$http.put(url, $scope.editing);
			}
			if (iix + 1 == getNumItems(rix, cix)) {
				$scope.rows[rix][columnName].push({patient: $scope.rows[rix].id});
			}
		}
	};

	$scope.saveEditAndAdd = function() {
		$scope.saveEdit();
		$scope.iix = getNumItems($scope.rix, $scope.cix) - 1;
		startEdit();
	}

	$scope.cancelAdd = function() {
		clearModal('add-new');
		editing = false;
	};

	$scope.cancelEdit = function() {
		var cix = $scope.cix;
		var columnName = $scope.columns[cix].name;

		clearModal(columnName);
		editing = false;
	};

	$scope.doDelete = function() {
		var rix = $scope.rix;
		var cix = $scope.cix;
		var iix = $scope.iix;
		var columnName = $scope.columns[cix].name;
		var id = $scope.rows[rix][columnName][iix].id

		url = 'patient/' + $scope.rows[rix].id + '/' + columnName + '/' + id + '/';
		$http.delete(url);

		$scope.rows[rix][columnName].splice(iix, 1);
		deleting = false;
	};

	$scope.cancelDelete = function() {
		deleting = false;
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

	$scope.mouseEnter = function(rix, cix) {
		$scope.mouseRix = rix;
		$scope.mouseCix = cix;
	}

	$scope.mouseLeave = function() {
		$scope.mouseRix = -1;
		$scope.mouseCix = -1;
	}

	function getNumItems(rix, cix) {
		var column = $scope.columns[cix];
		if (column.single) {
			return 1;
		} else {
			return $scope.rows[rix][column.name].length;
		}
	};

	$scope.keypress = function(e) {
		if (editing) {
			switch (e.keyCode) {
				case 27: // escape
					$scope.cancelEdit();
					break;
			}
		} else if (deleting) {
			// ignore all keystrokes here
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
				case 8: // backspace
					e.preventDefault();
				case 46: // delete
					startDelete();
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

app.value('$strapConfig', {
	datepicker: {
		format: 'yyyy-mm-dd',
		type: 'string'
	}
});
