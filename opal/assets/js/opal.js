var CATEGORIES = ['Inpatient', 'Followup', 'Review'];

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

var app = angular.module('opalApp', ['$strap.directives', 'ui.event']);

// See http://stackoverflow.com/questions/8302928/angularjs-with-django-conflicting-template-tags
app.config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('[[');
	$interpolateProvider.endSymbol(']]');
});

app.controller('TableCtrl', function($scope, $http, $filter) {
	var state = 'normal';

	$scope.rows = [];

	$scope.rix = 0; // row index
	$scope.cix = 0; // column index
	$scope.iix = 0; // item index

	$scope.mouseRix = -1; // index of row mouse is currently over
	$scope.mouseCix = -1; // index of column mouse is currently over

	$scope.currentTag = 'mine'; // initially retrieve patients of interest to current user
	$scope.query = {hospital: '', ward: ''};

	$http.get('schema/').success(function(data) {
		var option_lists = data.option_lists;
		var option_names = getKeys(option_lists);
		var option_name;
		var columnName;

		$scope.columns = data.columns;
		$scope.$watch('currentTag', getPatients);

		getPatients();

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

	function getPatients() {
		$http.get('patient/?tag=' + $scope.currentTag).success(function(rows) {
			for (var rix = 0; rix < rows.length; rix++) {
				for (var cix = 0; cix < $scope.columns.length; cix++) {
					columnName = $scope.columns[cix].name;
					if ($scope.columns[cix].single) {
						rows[rix][columnName] = [rows[rix][columnName]];
					} else {
						rows[rix][columnName].push({patient: rows[rix].id});
					}
				}
			}
			rows.sort(comparePatients);
			$scope.rows = rows;
		});
	};

	function comparePatients(p1, p2) {
		var v1, v2;
		var comparators = [
			function(p) { return CATEGORIES.indexOf(p.location[0].category) },
			function(p) { return p.location[0].hospital },
			function(p) {
				if (p.location[0].hospital == 'UCH' && p.location[0].ward.match(/^T\d+/)) {
					return parseInt(p.location[0].ward.substring(1));
				} else {
					return p.location[0].ward
			       	}
			},
			function(p) { return parseInt(p.location[0].bed) },
		];

		for (var ix = 0; ix < comparators.length; ix++) {
			v1 = comparators[ix](p1);
			v2 = comparators[ix](p2);
			if (v1 < v2) {
				return -1;
			} else if (v1 > v2) {
				return 1;
			}
		}

		return 0;
	};

	function getRowIxFromPatientId(patientId) {
		for (var rix = 0; rix < $scope.rows.length; rix++) {
			if ($scope.rows[rix].id == patientId) {
				return rix;
			}
		};
		return -1;
	};

	function getNumItems(rix, cix) {
		var column = $scope.columns[cix];
		return $scope.rows[rix][column.name].length;
	};

	function isSingleColumn(cix) {
		return $scope.columns[cix].single;
	};

	function getColumnName(cix) {
		return $scope.columns[cix].name;
	};

	function getCurrentColumnName(cix) {
		return getColumnName($scope.cix);
	};

	function getItem(rix, cix, iix) {
		var columnName = $scope.columns[cix].name;
		return $scope.rows[rix][columnName][iix];
	};

	function getCurrentItem() {
		return getItem($scope.rix, $scope.cix, $scope.iix);
	};

	function startEdit() {
		state = 'editing';
		$scope.editing = clone(getCurrentItem());
		$scope.editing.tags = clone($scope.rows[$scope.rix].tags);
		$scope.editingName = $scope.rows[$scope.rix].demographics[0].name;
		$('#' + getCurrentColumnName() + '-modal').modal();
		$('#' + getCurrentColumnName() + '-modal').find('input,textarea').first().focus();
	};

	function startDelete() {
		if (isSingleColumn($scope.cix)) {
			// Cannot delete singleton
			return;
		}

		if (getNumItems($scope.rix, $scope.cix) == $scope.iix + 1) {
			// Cannot delete 'Add'
			return;
		}

		state = 'deleting';
		$('#delete-confirmation').modal();
		$('#delete-confirmation').find('.btn-primary').focus();
	};

	function clearModal(columnName) {
		$('#' + columnName + '-modal').modal('hide')

		// See https://github.com/openhealthcare/opal/issues/28
		document.activeElement.blur();
	};

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

	$scope.startAdd = function() {
		state = 'adding';
		$scope.foundPatient = false; // Display rest of form when true
		$scope.findingPatient = false; // Disable Search button when true
		$scope.editing = {location: {}, demographics: {}, tags: {}};
		$('#add-new-modal').modal();
		$('#add-new-modal').find('input,textarea').first().focus();
	};

	$scope.findByHospitalNumber = function() {
		var hospitalNumber = $scope.editing.demographics.hospital_number
		$scope.findingPatient = true;
		$http.get('search/?hospital_number=' + hospitalNumber).success(function(results) {
			$scope.findingPatient = false;
			$scope.foundPatient = true; // misnomer: might not actually have found a patient!
			if (results.patients.length == 1) {
				$scope.editing.demographics = clone(results.patients[0].demographics);
				$scope.editing.location = clone(results.patients[0].location);
				$scope.editing.tags = clone(results.patients[0].tags);
			}
			$scope.editing.tags[$scope.currentTag] = true;
		});
	};

	$scope.saveAdd = function() {
		var rix;
		state = 'normal';
		clearModal('add-new');
		$http.post('patient/', $scope.editing).success(function(patient) {
			for (var cix = 0; cix < $scope.columns.length; cix++) {
				if (isSingleColumn(cix)) {
					patient[getColumnName(cix)] = [patient[getColumnName(cix)]];
				} else {
					patient[getColumnName(cix)] = [{patient: patient.id}];
				}
			}
			rix = getRowIxFromPatientId(patient.id);
			if (rix != -1) {
				// If patient is already in table, remove the corresponding row.
				// This guards against user changing patient data in add form.
				$scope.rows.splice(rix, 1);
			}
			$scope.rows.push(patient);
			$scope.rows.sort(comparePatients);
			$scope.selectItem(getRowIxFromPatientId(patient.id), 0, 0);
		});
	};

	$scope.saveEdit = function() {
		var columnName = getCurrentColumnName();
		var patientId = $scope.rows[$scope.rix].id;
		var url = 'patient/' + patientId + '/' + columnName + '/';
		var items = $scope.rows[$scope.rix][columnName];
		var newItemIx;

		state = 'normal';
		clearModal(columnName);

		items[$scope.iix] = clone($scope.editing);

		if (isSingleColumn($scope.cix)) {
			$http.put(url, $scope.editing);
			if (columnName == 'location') {
				$scope.rows.sort(comparePatients);
				$scope.selectItem(getRowIxFromPatientId(patientId), $scope.cix, 0);
			}
		} else {
			if (typeof($scope.editing.id) == 'undefined') {
				// This is a new item
				items.push({patient: patientId});
				newItemIx = $scope.iix;
				$http.post(url, $scope.editing).success(function(item) {
					items[newItemIx].id = item.id;
				});
			} else {
				url = url + $scope.editing.id + '/';
				$http.put(url, $scope.editing);
			}
		}
	};

	$scope.saveEditAndAdd = function() {
		$scope.saveEdit();
		$scope.iix = getNumItems($scope.rix, $scope.cix) - 1;
		startEdit();
	}

	$scope.cancelAdd = function() {
		state = 'normal';
		clearModal('add-new');
	};

	$scope.cancelEdit = function() {
		state = 'normal';
		clearModal(getCurrentColumnName());
	};

	$scope.doDelete = function() {
		var patientId = $scope.rows[$scope.rix].id;
		var columnName = getCurrentColumnName();
		var items = $scope.rows[$scope.rix][columnName];
		var itemId = items[$scope.iix].id;
		var url = 'patient/' + patientId + '/' + columnName + '/' + itemId + '/';

		$http.delete(url);

		items.splice($scope.iix, 1);
		state = 'normal';
	};

	$scope.cancelDelete = function() {
		state = 'normal';
	};

	$scope.selectItem = function(rix, cix, iix) {
		$scope.rix = rix;
		$scope.cix = cix;
		$scope.iix = iix;
		state = 'normal';
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

	$scope.focusOnQuery = function() {
		$scope.selectItem(-1, -1, -1);
		state = 'searching';
	}

	$scope.search = function (patient) {
		if (patient.location[0].hospital.toLowerCase().indexOf($scope.query.hospital.toLowerCase()) == -1) {
			return false;
		}
		if (patient.location[0].ward.toLowerCase().indexOf($scope.query.ward.toLowerCase()) == -1) {
			return false;
		}
		return true;
	}

	$scope.keypress = function(e) {
		switch (state) {
			case 'adding':
				handleKeypressAdd(e);
				break;
			case 'editing':
				handleKeypressEdit(e);
				break;
			case 'deleting':
				handleKeypressDelete(e);
				break;
			case 'searching':
				// nothing special
				break;
			case 'normal':
				handleKeypressNormal(e);
				break;
		}
	}

	function handleKeypressAdd(e) {
		if (e.keyCode == 27) { // escape
			$scope.cancelAdd();
		}
	}


	function handleKeypressEdit(e) {
		if (e.keyCode == 27) { // escape
			$scope.cancelEdit();
		}
	}


	function handleKeypressDelete(e) {
		if (e.keyCode == 27) { // escape
			$scope.cancelDelete();
		}
	}

	function handleKeypressNormal(e) {
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

// This is unlikely to be idiomatic
app.controller('PatientCtrl', function($scope, $http) {
	var patientId = window.location.href.split('/').slice(-2)[0];

	$http.get('/schema/').success(function(data) {
		$scope.columns = data.columns;

		$http.get('/patient/').success(function(patients) {
			var patient;
			var columnName;

			for (var pix = 0; pix < patients.length; pix++) {
				if (patients[pix].id == patientId) {
					patient = patients[pix];
					break;
				}
			}

			for (var cix = 0; cix < $scope.columns.length; cix++) {
				columnName = $scope.columns[cix].name;
				if ($scope.columns[cix].single) {
					patient[columnName] = [patient[columnName]];
				}
			}
			$scope.patient = patient;
		});
	})

	$scope.getSynonymn = function(option, term) {
		return term;
	};
});

app.value('$strapConfig', {
	datepicker: {
		format: 'yyyy-mm-dd',
		type: 'string'
	}
});
