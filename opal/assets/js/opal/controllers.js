var CATEGORIES = ['Inpatient', 'Review', 'Followup', 'Transferred', 'Discharged', 'Deceased'];

var controllers = angular.module('opal.controllers', [
	'ngCookies',
       	'opal.services',
       	'$strap.directives',
       	'ui.event'
]);

function replaceSynonym($scope, option, term){
    if(!term){
        return term
    }
    _.each(_.pairs($scope.synonyms[option]), function(synonym){
        var possible = synonym[0];
        var canonical = synonym[1]
        term = term.replace(possible, canonical);
    });
    return term
}

controllers.controller('RootCtrl', function($scope) {
	$scope.keydown = function(e) {
		$scope.$broadcast('keydown', e);
	};
});

controllers.controller('PatientListCtrl', function($scope, $http, $cookieStore, schema, patients) {
	var state = 'normal';
	var columnName;
	var newItem;

	$scope.rix = 0; // row index
	$scope.cix = 0; // column index
	$scope.iix = 0; // item index

	$scope.mouseRix = -1; // index of row mouse is currently over
	$scope.mouseCix = -1; // index of column mouse is currently over

	$scope.query = {hospital: '', ward: ''};
	$scope.currentTag = $cookieStore.get('opal.currentTag') || 'mine'; // initially display patients of interest to current user

	$scope.columns = []
	for (var cix = 0; cix < schema.columns.length; cix++) {
		if (schema.columns[cix].name != 'microbiology_input') {
			$scope.columns.push(schema.columns[cix]);
		}
	}

	$scope.synonyms = schema.synonyms;

	$scope.microbiology_test_list = [];

	// The following could be done on the server
	for (var optionName in schema.option_lists) {
		if (optionName.indexOf('micro_test') == 0) {
			for (var oix = 0; oix < schema.option_lists[optionName].length; oix++) {
				$scope.microbiology_test_list.push(schema.option_lists[optionName][oix]);
			}
		} else {
			$scope[optionName + '_list'] = schema.option_lists[optionName];
		}
	};

	$scope.patient_category_list = ['Inpatient', 'Review'];

	for (var pix = 0; pix < patients.length; pix++) {
		for (var cix = 0; cix < $scope.columns.length; cix++) {
			columnName = $scope.columns[cix].name;
			if (!isSingleColumn(cix)) {
				newItem = {patient: patients[pix].id};
				if (columnName == 'microbiology_test') {
					newItem.date_ordered = getTodaysDate();
				}
				if (columnName == 'general_note') {
					newItem.date = getTodaysDate();
				}
				if (columnName == 'antimicrobial') {
					newItem.start_date = getTodaysDate();
				}
                                if (columnName == 'diagnosis') {
                                        newItem.date_of_diagnosis = getTodaysDate();
                                }
				patients[pix][columnName].push(newItem);
			};
		};
	};

	$scope.patients = patients;

	$scope.rows = getVisiblePatients();

	function getVisiblePatients() {
		var patient;
		var patients = []
		for (var pix = 0; pix < $scope.patients.length; pix++) {
			patient = $scope.patients[pix]
			if (patient.tags[$scope.currentTag] != true) {
				continue;
			}
			if (patient.location[0].hospital.toLowerCase().indexOf($scope.query.hospital.toLowerCase()) == -1) {
				continue;
			}
			if (patient.location[0].ward.toLowerCase().indexOf($scope.query.ward.toLowerCase()) == -1) {
				continue;
			}
			patients.push(patient);
		}
		patients.sort(comparePatients);
		return patients;
	};

	$scope.$watch('currentTag', function() {
		$cookieStore.put('opal.currentTag', $scope.currentTag);
		$scope.rows = getVisiblePatients();
		$scope.rix = 0;
	});

	$scope.$watch('query.hospital', function() {
		$scope.rows = getVisiblePatients();
	});

	$scope.$watch('query.ward', function() {
		$scope.rows = getVisiblePatients();
	});

	$scope.$on('keydown', function(event, originalEvent) {
		switch (state) {
			case 'adding':
				handleKeypressAdd(originalEvent);
				break;
			case 'editing':
				handleKeypressEdit(originalEvent);
				break;
			case 'deleting':
				handleKeypressDelete(originalEvent);
				break;
			case 'discharging':
				handleKeypressDischarge(originalEvent);
				break;
			case 'searching':
				// nothing special
				break;
			case 'normal':
				handleKeypressNormal(originalEvent);
				break;
		};
	});

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

	$scope.getSynonymn = function(option, term) {
            return replaceSynonym($scope, option, term);
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

	function clearModal(columnName) {
		$('#' + columnName + '-modal').modal('hide')

		// See https://github.com/openhealthcare/opal/issues/28
		$(".btn").blur();
	};

	$scope.print = function() {
		window.print();
	};

	$scope.startAdd = function() {
		state = 'adding';
		$scope.foundPatient = false; // Display rest of form when true
		$scope.findingPatient = false; // Disable Search button when true
		$scope.editing = {
			location: {date_of_admission: getTodaysDate()},
			demographics: {},
			tags: {}
		};
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

	$scope.selectItem = function(rix, cix, iix) {
		$scope.rix = rix;
		$scope.cix = cix;
		$scope.iix = iix;
		state = 'normal';
	}

	$scope.saveAdd = function() {
		var rix;
		state = 'normal';
		clearModal('add-new');
		$http.post('patient/', $scope.editing).success(function(patient) {
			for (var cix = 0; cix < $scope.columns.length; cix++) {
				if (!isSingleColumn(cix)) {
					// TODO ensure date fields are set up
					patient[getColumnName(cix)] = [{patient: patient.id}];
				}
			}
			rix = getRowIxFromPatientId(patient.id);
			if (rix != -1) {
				// If patient is already in table, remove the corresponding row.
				// This guards against user changing patient data in add form.
				$scope.rows.splice(rix, 1);
			}
			$scope.patients.push(patient);
			$scope.rows = getVisiblePatients();
			$scope.selectItem(getRowIxFromPatientId(patient.id), 0, 0);
		});
	};

	$scope.cancelAdd = function() {
		state = 'normal';
		clearModal('add-new');
	};

	function startEdit() {
		state = 'editing';
		$scope.editing = clone(getCurrentItem());
		$scope.editing.tags = clone($scope.rows[$scope.rix].tags);
		$scope.editingName = $scope.rows[$scope.rix].demographics[0].name;
		$('#' + getCurrentColumnName() + '-modal').modal();
		$('#' + getCurrentColumnName() + '-modal').find('input,textarea').first().focus();
	};

	$scope.saveEdit = function() {
		var columnName = getCurrentColumnName();
		var patientId = $scope.rows[$scope.rix].id;
		var url = 'patient/' + patientId + '/' + columnName + '/';
		var items = $scope.rows[$scope.rix][columnName];
		var newItem;
		var newItemIx;

		state = 'normal';
		clearModal(columnName);

		items[$scope.iix] = clone($scope.editing);

		if (isSingleColumn($scope.cix)) {
			url = url + $scope.editing.id + '/';
			$http.put(url, $scope.editing);
			if (columnName == 'location') {
				$scope.rows[$scope.rix].tags = $scope.editing.tags;
				$scope.rows = getVisiblePatients();
				$scope.selectItem(getRowIxFromPatientId(patientId), $scope.cix, 0);
			}
		} else {
			if (typeof($scope.editing.id) == 'undefined') {
				// This is a new item
				newItem = {patient: patientId};
				if (columnName == 'microbiology_test') {
					newItem.date_ordered = getTodaysDate();
				}
				if (columnName == 'general_note') {
					newItem.date = getTodaysDate();
				}
				if (columnName == 'antimicrobial') {
					newItem.start_date = getTodaysDate();
				}
                                if (columnName == 'diagnosis') {
                                        newItem.date_of_diagnosis = getTodaysDate();
                                }
				items.push(newItem);
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

	$scope.cancelEdit = function() {
		state = 'normal';
		clearModal(getCurrentColumnName());
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

	$scope.doDelete = function() {
		var patientId = $scope.rows[$scope.rix].id;
		var columnName = getCurrentColumnName();
		var items = $scope.rows[$scope.rix][columnName];
		var itemId = items[$scope.iix].id;
		var url = 'patient/' + patientId + '/' + columnName + '/' + itemId + '/';

		$http['delete'](url);

		items.splice($scope.iix, 1);
		state = 'normal';
	};

	$scope.cancelDelete = function() {
		state = 'normal';
	};

	$scope.startDischarge = function(rix, event) {
		var patient = $scope.rows[rix];
		var currentCategory = patient.location[0].category;
		var newCategory;

		event.preventDefault();

		if (currentCategory == 'Inpatient') {
			newCategory = 'Discharged';
		} else if (currentCategory == 'Review' || currentCategory == 'Followup') {
			newCategory = 'Unfollow';
		} else {
			newCategory = currentCategory;
		}

		state = 'discharging';
		$scope.discharge = {
			rix: rix,
			category: newCategory,
			date: getTodaysDate()
		};
		$('#discharge-confirmation-modal').modal();
		$('#discharge-confirmation-modal').find('input,textarea').first().focus();
	};

	$scope.doDischarge = function() {
		var discharge = $scope.discharge;
		var patient = $scope.rows[discharge.rix];
		var location = patient.location[0];
		var editing = clone(location);
		var url = 'patient/' + patient.id + '/location/';

		if (discharge.category != 'Unfollow') {
			editing.category = discharge.category;
			editing.discharge_date = discharge.date;
		};

		editing.tags = clone(patient.tags);
		if (discharge.category != 'Followup') {
			editing.tags[$scope.currentTag] = false;
		};

		$http.put(url, editing).success(function(response) {
			state = 'normal';
			clearModal('discharge-confirmation');
			location.category = editing.category;
			location.discharge_date = editing.discharge_date;
			patient.tags = clone(editing.tags);
			$scope.rows = getVisiblePatients();
			$scope.selectItem(0, $scope.cix, 0);
		});
	};

	$scope.cancelDischarge = function() {
		state = 'normal';
		clearModal('discharge-confirmation');
	};

	$scope.focusOnQuery = function() {
		$scope.selectItem(-1, -1, -1);
		state = 'searching';
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

	function handleKeypressAdd(e) {
		if (e.keyCode == 27) { // escape
			$scope.cancelAdd();
		};
	};

	function handleKeypressEdit(e) {
		if (e.keyCode == 27) { // escape
			$scope.cancelEdit();
		};
	};

	function handleKeypressDelete(e) {
		if (e.keyCode == 27) { // escape
			$scope.cancelDelete();
		};
	};

	function handleKeypressDischarge(e) {
		if (e.keyCode == 27) { // escape
			$scope.cancelDischarge();
		};
	};

	function handleKeypressNormal(e) {
		switch (e.keyCode) {
			case 37: // left
				goLeft();
				break;
			case 39: // right
				goRight();
				break;
			case 38: // up
				goUp();
				break;
			case 40: // down
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
                        case 113: // F2
                                startEdit();
		};
	};

	function goLeft() {
		if ($scope.cix > 0) {
			$scope.cix--;
			$scope.iix = 0;
		};
	};

	function goRight() {
		if ($scope.cix < $scope.columns.length - 1) {
			$scope.cix++;
			$scope.iix = 0;
		};
	};

	function goUp() {
		if ($scope.iix > 0) {
			$scope.iix--;
		} else {
			if ($scope.rix > 0) {
				$scope.rix--;
				$scope.iix = getNumItems($scope.rix, $scope.cix) - 1;
			};
		};
	};

	function goDown() {
		if ($scope.iix < getNumItems($scope.rix, $scope.cix) - 1) {
			$scope.iix++;
		} else {
			if ($scope.rix < $scope.rows.length - 1) {
				$scope.rix++;
				$scope.iix = 0;
			};
		};
	};

});

controllers.controller('PatientDetailCtrl', function($scope, $http, schema, patient) {
	var state = 'normal';
	var columnName;
	var newItem;

	$scope.cix = 0; // column index (although columns are arranged vertically...)
	$scope.iix = 0; // item index

	$scope.mouseCix = -1; // index of column mouse is currently over

	$scope.columns = schema.columns;
	$scope.synonyms = schema.synonyms;

	$scope.microbiology_test_list = [];

	// The following could be done on the server
	for (var optionName in schema.option_lists) {
		if (optionName.indexOf('micro_test') == 0) {
			for (var oix = 0; oix < schema.option_lists[optionName].length; oix++) {
				$scope.microbiology_test_list.push(schema.option_lists[optionName][oix]);
			}
		} else {
			$scope[optionName + '_list'] = schema.option_lists[optionName];
		}
	};

	$scope.patient_category_list = ['Inpatient', 'Review'];

	for (var cix = 0; cix < $scope.columns.length; cix++) {
		columnName = $scope.columns[cix].name;
		if (!isSingleColumn(cix)) {
			newItem = {patient: patient.id};
			if (columnName == 'microbiology_test') {
				newItem.date_ordered = getTodaysDate();
			}
			if (columnName == 'general_note') {
				newItem.date = getTodaysDate();
			}
			if (columnName == 'antimicrobial') {
				newItem.start_date = getTodaysDate();
			}
			if (columnName == 'microbiology_input') {
				newItem.date = getTodaysDate();
			}
			patient[columnName].push(newItem);
		};
	}

	$scope.patient = patient;

	$scope.$on('keydown', function(event, originalEvent) {
		switch (state) {
			case 'editing':
				handleKeypressEdit(originalEvent);
				break;
			case 'deleting':
				handleKeypressDelete(originalEvent);
				break;
			case 'searching':
				// nothing special
				break;
			case 'normal':
				handleKeypressNormal(originalEvent);
				break;
		};
	});

	$scope.getSynonymn = function(option, term) {
            return replaceSynonym($scope, option, term);
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

	function getItem(cix, iix) {
		var columnName = $scope.columns[cix].name;
		return $scope.patient[columnName][iix];
	};

	function getCurrentItem() {
		return getItem($scope.cix, $scope.iix);
	};

	function getNumItems(cix) {
		var column = $scope.columns[cix];
		return $scope.patient[column.name].length;
	};

	function clearModal(columnName) {
		$('#' + columnName + '-modal').modal('hide')

		// See https://github.com/openhealthcare/opal/issues/28
		$(".btn").blur();
	};

	$scope.mouseEnter = function(cix) {
		$scope.mouseCix = cix;
	}

	$scope.mouseLeave = function() {
		$scope.mouseRix = -1;
		$scope.mouseCix = -1;
	}

	function startEdit() {
		state = 'editing';
		$scope.editing = clone(getCurrentItem());
		$scope.editing.tags = clone($scope.patient.tags);
		$scope.editingName = $scope.patient.demographics[0].name;
		$('#' + getCurrentColumnName() + '-modal').modal();
		$('#' + getCurrentColumnName() + '-modal').find('input,textarea').first().focus();
	};

	$scope.saveEdit = function() {
		var columnName = getCurrentColumnName();
		var patientId = $scope.patient.id;
		var url = 'patient/' + patientId + '/' + columnName + '/';
		var items = $scope.patient[columnName];
		var newItemIx;

		state = 'normal';
		clearModal(columnName);

		items[$scope.iix] = clone($scope.editing);

		if (isSingleColumn($scope.cix)) {
			url = url + $scope.editing.id + '/';
			$http.put(url, $scope.editing);
			if (columnName == 'location') {
				$scope.patient.tags = $scope.editing.tags;
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
		$scope.iix = getNumItems($scope.cix) - 1;
		startEdit();
	}

	$scope.cancelEdit = function() {
		state = 'normal';
		clearModal(getCurrentColumnName());
	};

	function startDelete() {
		if (isSingleColumn($scope.cix)) {
			// Cannot delete singleton
			return;
		}

		if (getNumItems($scope.cix) == $scope.iix + 1) {
			// Cannot delete 'Add'
			return;
		}

		state = 'deleting';
		$('#delete-confirmation').modal();
		$('#delete-confirmation').find('.btn-primary').focus();
	};

	$scope.doDelete = function() {
		var patientId = $scope.patient.id;
		var columnName = getCurrentColumnName();
		var items = $scope.patient[columnName];
		var itemId = items[$scope.iix].id;
		var url = 'patient/' + patientId + '/' + columnName + '/' + itemId + '/';

		$http['delete'](url);

		items.splice($scope.iix, 1);
		state = 'normal';
	};

	$scope.cancelDelete = function() {
		state = 'normal';
	};

	$scope.selectItem = function(cix, iix) {
		$scope.cix = cix;
		$scope.iix = iix;
		state = 'normal';
	};

	$scope.editItem = function(cix, iix) {
		$scope.selectItem(cix, iix);
		startEdit();
	}

	function handleKeypressEdit(e) {
		if (e.keyCode == 27) { // escape
			$scope.cancelEdit();
		};
	};

	function handleKeypressDelete(e) {
		if (e.keyCode == 27) { // escape
			$scope.cancelDelete();
		};
	};

	function handleKeypressNormal(e) {
		switch (e.keyCode) {
			case 38: // up
				goUp();
				break;
			case 40: // down
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
		};
	};

	function goUp() {
		if ($scope.iix > 0) {
			$scope.iix--;
		} else {
			if ($scope.cix > 0) {
				$scope.cix--;
				$scope.iix = getNumItems($scope.cix) - 1;
			};
		};
	};

	function goDown() {
		if ($scope.iix < getNumItems($scope.cix) - 1) {
			$scope.iix++;
		} else {
			if ($scope.cix < $scope.columns.length - 1) {
				$scope.cix++;
				$scope.iix = 0;
			};
		};
	};
});

controllers.controller('SearchCtrl', function($scope, $http, $location) {
	$scope.searchTerms = {
		hospital_number: '',
		name: '',
	};
	$scope.results = [];
	$scope.searched = false;

	$scope.patient_category_list = ['Inpatient', 'Review'];
	$scope.hospital_list = ['Heart Hospital', 'NHNN', 'UCH'];

	$scope.doSearch = function() {
		var queryParams = [];
		var queryString;

		for (var term in $scope.searchTerms) {
			if ($scope.searchTerms[term] != '') {
				queryParams.push(term + '=' + $scope.searchTerms[term]);
			};
		};

		if (queryParams.length == 0) {
			return;
		};

		queryString = queryParams.join('&');

		$http.get('search/?' + queryString).success(function(results) {
			$scope.searched = true;
			$scope.results = results.patients;
		});
	};

	$scope.startAdd = function() {
		$scope.editing = {
			location: {date_of_admission: getTodaysDate()},
		       	demographics: {},
		       	tags: {}
		};
		if ($scope.results.length == 0) {
			$scope.editing.demographics.name = $scope.searchTerms.name;
			$scope.editing.demographics.hospital_number = $scope.searchTerms.hospital_number;
		}
		$('#add-new-modal').modal();
		$('#add-new-modal').find('input,textarea').first().focus();
	}

	$scope.findByHospitalNumber = function() {
		var hospitalNumber = $scope.editing.demographics.hospital_number
		$http.get('search/?hospital_number=' + hospitalNumber).success(function(results) {
			$scope.foundPatient = true; // misnomer: might not actually have found a patient!
			if (results.patients.length == 1) {
				$scope.editing.demographics = clone(results.patients[0].demographics);
				$scope.editing.location = clone(results.patients[0].location);
				$scope.editing.tags = clone(results.patients[0].tags);
			}
			$scope.editing.tags[$scope.currentTag] = true;
		});
	};

	function clearModal(columnName) {
		$('#' + columnName + '-modal').modal('hide')

		// See https://github.com/openhealthcare/opal/issues/28
		$(".btn").blur();
	};

	$scope.saveAdd = function() {
		clearModal('add-new');
		$http.post('patient/', $scope.editing).success(function(patient) {
			$location.path('patient/' + patient.id);
		});
	};

	$scope.cancelAdd = function() {
		state = 'normal';
		clearModal('add-new');
	};
});
