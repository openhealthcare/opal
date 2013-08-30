var controllers = angular.module('opal.controllers', [
	'ngCookies',
	'opal.services',
	'ui.event',
	'ui.bootstrap'
]);

controllers.controller('RootCtrl', function($scope) {
	$scope.keydown = function(e) {
		$scope.$broadcast('keydown', e);
	};
});

controllers.controller('PatientListCtrl', function($scope, $cookieStore, $dialog, Patient, schema, patients, options) {
	$scope.state = 'normal';

	$scope.rix = 0; // row index
	$scope.cix = 0; // column index
	$scope.iix = 0; // item index

	$scope.mouseRix = -1; // index of row mouse is currently over
	$scope.mouseCix = -1; // index of column mouse is currently over

	$scope.query = {hospital: '', ward: ''};
	$scope.currentTag = $cookieStore.get('opal.currentTag') || 'mine'; // initially display patients of interest to current user
    $scope.currentSubTag = 'all';
    $cookieStore.put('opal.currentSubTag', 'all');

	$scope.columns = schema.columns;

	$scope.rows = getVisiblePatients();

	function getVisiblePatients() {
		var visiblePatients = [];

		for (var pix in patients) {
			if (patients[pix].isVisible($scope.currentTag, $scope.currentSubTag,
                                        $scope.query.hospital, $scope.query.ward)) {
				visiblePatients.push(patients[pix]);
			};
		};

		visiblePatients.sort(comparePatients);
		return visiblePatients;
	};

	function comparePatients(p1, p2) {
		return p1.compare(p2);
	};

	$scope.$watch('currentTag', function() {
		$cookieStore.put('opal.currentTag', $scope.currentTag);
        $scope.currentSubTag = 'all';
		$scope.rows = getVisiblePatients();
		$scope.rix = 0;
	});

    $scope.$watch('currentSubTag', function(){
		$cookieStore.put('opal.currentSubTag', $scope.currentSubTag);
        $scope.rows =  getVisiblePatients();
        $scope.rix =  0;
    });

    $scope.showSubtags = function(withsubtags){
        var show =  _.contains(withsubtags, $scope.currentTag);
        return show
    };

	$scope.$watch('query.hospital', function() {
		$scope.rows = getVisiblePatients();
	});

	$scope.$watch('query.ward', function() {
		$scope.rows = getVisiblePatients();
	});

	$scope.$on('keydown', function(event, e) {
		if ($scope.state == 'normal') {
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
				case 113: // F2
					$scope.editItem($scope.rix, $scope.cix, $scope.iix);
                    e.preventDefault();
					break;
				case 8: // backspace
					e.preventDefault();
				case 46: // delete
					$scope.deleteItem($scope.rix, $scope.cix, $scope.iix);
					break;
				case 191: // question mark
					if(e.shiftKey){
						showKeyboardShortcuts();
					}
					break;
			};
		};
	});

	function getColumnName(cix) {
		return $scope.columns[cix].name;
	};

	function getRowIxFromPatientId(patientId) {
		for (var rix = 0; rix < $scope.rows.length; rix++) {
			if ($scope.rows[rix].id == patientId) {
				return rix;
			}
		};
		return -1;
	};

	function getPatient(rix) {
		return $scope.rows[rix];
	};

	$scope.print = function() {
		window.print();
	};

	$scope.selectItem = function(rix, cix, iix) {
		$scope.rix = rix;
		$scope.cix = cix;
		$scope.iix = iix;
	};

	$scope.focusOnQuery = function() {
		$scope.selectItem(-1, -1, -1);
		$scope.state = 'search';
	};

	$scope.blurOnQuery = function() {
		if ($scope.rix == -1) {
			$scope.selectItem(0, 0, 0);
		};
		$scope.state = 'normal';
	};

	$scope.addPatient = function() {
		var modal;
		$scope.state = 'modal';

		modal = $dialog.dialog({
			templateUrl: '/templates/modals/add_patient.html/',
			controller: 'AddPatientCtrl',
			resolve: {
				details: function() { return { currentTag: $scope.currentTag };},
				schema: function() { return schema; },
				options: function() { return options; },
			}
		});

		modal.open().then(function(result) {
			var patient;
			$scope.state = 'normal';

			if (angular.isObject(result)) {
				// result is attributes of patient
				patient = new Patient(result, schema)
				patients[patient.id] = patient;
				$scope.rows = getVisiblePatients();
				$scope.selectItem(getRowIxFromPatientId(patient.id), 0, 0);
			}
		});
	};

	$scope.dischargePatient = function(rix, event) {
		var modal;
		var patient = getPatient(rix);

		// This is required to prevent the page reloading
		event.preventDefault();

		$scope.state = 'modal';

		modal = $dialog.dialog({
			templateUrl: '/templates/modals/discharge_patient.html/',
			controller: 'DischargePatientCtrl',
			resolve: {
				patient: function() { return patient; },
				currentTag: function() { return $scope.currentTag; },
			}
		});

		modal.open().then(function(result) {
			$scope.state = 'normal';

			if (result == 'discharged') {
				$scope.rows = getVisiblePatients();
				$scope.selectItem(0, $scope.cix, 0);
			};
		});
	};

	$scope.editItem = function(rix, cix, iix) {
		var modal;
		var columnName = getColumnName(cix);
		var patient = getPatient(rix);
		var item;

		if (iix == patient.getNumberOfItems(columnName)) {
			item = patient.newItem(columnName);
		} else {
			item = patient.getItem(columnName, iix);
		}

		$scope.selectItem(rix, cix, iix);
		$scope.state = 'modal';

		modal = $dialog.dialog({
			templateUrl: '/templates/modals/' + columnName + '.html/',
			controller: 'EditItemCtrl',
			resolve: {
				item: function() { return item; },
				options: function() { return options; },
			},
		});

		modal.open().then(function(result) {
			$scope.state = 'normal';

			if (columnName == 'location') {
				// User may have removed current tag
				$scope.rows = getVisiblePatients();
				$scope.selectItem(getRowIxFromPatientId(patient.id), $scope.cix, 0);
			}

			if (result == 'save-and-add-another') {
				$scope.editItem(rix, cix, patient.getNumberOfItems(columnName));
			};
		});
	};

	$scope.deleteItem = function(rix, cix, iix) {
		var modal;
		var columnName = getColumnName(cix);
		var patient = getPatient(rix);
		var item = patient.getItem(columnName, iix);

		if (schema.isSingleton(columnName)) {
			// Cannot delete singleton
			return;
		}

		if (!angular.isDefined(item)) {
			// Cannot delete 'Add'
			return;
		}

		$scope.state = 'modal'
		modal = $dialog.dialog({
			templateUrl: '/templates/modals/delete_item_confirmation.html/',
			controller: 'DeleteItemConfirmationCtrl',
			resolve: {
				item: function() { return item; },
			},
		});

		modal.open().then(function(result) {
			$scope.state = 'normal';
		});
	};

	$scope.mouseEnter = function(rix, cix) {
		$scope.mouseRix = rix;
		$scope.mouseCix = cix;
	}

	$scope.mouseLeave = function() {
		$scope.mouseRix = -1;
		$scope.mouseCix = -1;
	}

        function showKeyboardShortcuts(){
		// TODO fix this
                $('#keyboard-shortcuts').modal();
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
		var patient;
		var columnName = getColumnName($scope.cix);

		if ($scope.iix > 0) {
			$scope.iix--;
		} else if ($scope.rix > 0) {
			$scope.rix--;
			if (schema.isSingleton(columnName)) {
				$scope.iix = 0;
			} else {
				patient = getPatient($scope.rix);
				$scope.iix = patient.getNumberOfItems(columnName);
			};
		};
	};

	function goDown() {
		var patient = getPatient($scope.rix);
		var columnName = getColumnName($scope.cix);

		if (!schema.isSingleton(columnName) &&
		    ($scope.iix < patient.getNumberOfItems(columnName))) {
			$scope.iix++;
		} else if ($scope.rix < $scope.rows.length - 1) {
			$scope.rix++;
			$scope.iix = 0;
		};
	};
});

controllers.controller('PatientDetailCtrl', function($scope, $http, $dialog, schema, patient, options) {
	$scope.state = 'normal';

	$scope.cix = 0; // column index
	$scope.iix = 0; // item index

	$scope.mouseCix = -1; // index of column mouse is currently over

	$scope.patient = patient;

	$scope.columns = schema.columns;

	$scope.$on('keydown', function(event, e) {
		if ($scope.state == 'normal') {
			switch (e.keyCode) {
				case 38: // up
					goUp();
					break;
				case 40: // down
					goDown();
					break;
				case 13: // enter
				case 113: // F2
					$scope.editItem($scope.cix, $scope.iix);
					break;
				case 8: // backspace
					e.preventDefault();
				case 46: // delete
					$scope.deleteItem($scope.cix, $scope.iix);
					break;
				case 191: // question mark
					if(e.shiftKey){
						showKeyboardShortcuts();
					}
					break;
			};
		};
	});

	function getColumnName(cix) {
		return $scope.columns[cix].name;
	};

	$scope.selectItem = function(cix, iix) {
		$scope.cix = cix;
		$scope.iix = iix;
	};

	$scope.editItem = function(cix, iix) {
		var modal;
		var columnName = getColumnName(cix);
		var item;

		if (iix == patient.getNumberOfItems(columnName)) {
			item = patient.newItem(columnName);
		} else {
			item = patient.getItem(columnName, iix);
		}

		$scope.selectItem(cix, iix);
		$scope.state = 'modal';

		modal = $dialog.dialog({
			templateUrl: '/templates/modals/' + columnName + '.html/',
			controller: 'EditItemCtrl',
			resolve: {
				item: function() { return item; },
				options: function() { return options; },
			},
		});

		modal.open().then(function(result) {
			$scope.state = 'normal';

			if (result == 'add-another') {
				$scope.editItem(cix, patient.getNumberOfItems(columnName));
			};
		});
	};

	$scope.deleteItem = function(cix, iix) {
		var modal;
		var columnName = getColumnName(cix);
		var item = patient.getItem(columnName, iix);

		if (schema.isSingleton(columnName)) {
			// Cannot delete singleton
			return;
		}

		if (!angular.isDefined(item)) {
			// Cannot delete 'Add'
			return;
		}

		$scope.state = 'modal'
		modal = $dialog.dialog({
			templateUrl: '/templates/modals/delete_item_confirmation.html/',
			controller: 'DeleteItemConfirmationCtrl',
			resolve: {
				item: function() { return item; },
			},
		});

		modal.open().then(function(result) {
			$scope.state = 'normal';
		});
	};

	$scope.mouseEnter = function(cix) {
		$scope.mouseCix = cix;
	}

	$scope.mouseLeave = function() {
		$scope.mouseCix = -1;
	}

	function goUp() {
		var columnName;

		if ($scope.iix > 0) {
			$scope.iix--;
		} else {
			if ($scope.cix > 0) {
				$scope.cix--;
				columnName = getColumnName($scope.cix);
				if (schema.isSingleton(columnName)) {
					$scope.iix = 0;
				} else {
					$scope.iix = patient.getNumberOfItems(columnName);
				};
			};
		};
	};

	function goDown() {
		var columnName = getColumnName($scope.cix);

		if (!schema.isSingleton(columnName) &&
		    ($scope.iix < patient.getNumberOfItems(columnName))) {
			$scope.iix++;
		} else if ($scope.cix < $scope.columns.length - 1) {
			$scope.cix++;
			$scope.iix = 0;
		};
	};
});

controllers.controller('SearchCtrl', function($scope, $http, $location, $dialog, schema, options) {
	$scope.searchTerms = {
		hospital_number: '',
		name: '',
	};
	$scope.results = [];
	$scope.searched = false;

	$scope.patient_category_list = ['Inpatient', 'Outpatient', 'Review'];
	$scope.hospital_list = ['Heart Hospital', 'NHNN', 'UCH'];

	$scope.search = function() {
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

		$http.get('patient/?' + queryString).success(function(results) {
			$scope.searched = true;
			$scope.results = results;
		});
	};

	$scope.addPatient = function() {
		var modal, details;
		$scope.state = 'modal';

		if ($scope.results.length == 0) {
			details = {
				name: $scope.searchTerms.name,
				hospitalNumber: $scope.searchTerms.hospital_number,
			};
		} else {
			details = {};
		};

		modal = $dialog.dialog({
			templateUrl: '/templates/modals/add_patient.html/',
			controller: 'AddPatientCtrl',
			resolve: {
				details: function() { return details; },
				schema: function() { return schema; },
				options: function() { return options; },
			}
		});

		modal.open().then(function(result) {
			$scope.state = 'normal';

			if (angular.isObject(result)) {
				// result is attributes of patient
				$location.path('patient/' + result.id);
			}
		});
	};
});

controllers.controller('AddPatientCtrl', function($scope, $http, $cookieStore,
                                                  $timeout, dialog, Patient,
                                                  schema, options, details) {
    // initially display patients of interest to current user
    $scope.currentTag = $cookieStore.get('opal.currentTag') || 'mine';
    $scope.currentSubTag = $cookieStore.get('opal.currentSubTag') || 'all';

	$timeout(function() {
		dialog.modalEl.find('input,textarea').first().focus();
	});


	for (var name in options) {
		$scope[name + '_list'] = options[name];
	};
	$scope.patient_category_list = ['Inpatient', 'Outpatient', 'Review'];

	$scope.foundPatient = false; // Display rest of form when true
	$scope.findingPatient = false; // Disable Search button when true

	$scope.editing = {
		location: {
			date_of_admission: moment().format('DD/MM/YYYY'),
			tags: {},
		},
		demographics: {
			hospital_number: details.hospitalNumber,
			name: details.name,
		},
	};
    $scope.editing.location.tags[$scope.currentTag] = true;
    if($scope.currentSubTag != 'all'){
        $scope.editing.location.tags[$scope.currentSubTag] = true;
    }

    $scope.showSubtags = function(withsubtags){
        var show =  _.some(withsubtags, function(tag){ return $scope.editing.location.tags[tag] });
        return show
    };

    $scope.findByHospitalNumber = function() {
		var patient;
		var hospitalNumber = $scope.editing.demographics.hospital_number;
		$scope.findingPatient = true;
		$http.get('patient/?hospital_number=' + hospitalNumber).success(function(results) {
			$scope.findingPatient = false;
			$scope.foundPatient = true; // misnomer: might not actually have found a patient!
			if (results.length == 1) {
				patient = new Patient(results[0], schema);
				$scope.editing.demographics = patient.getItem('demographics', 0).makeCopy();
				$scope.editing.location = patient.getItem('location', 0).makeCopy();
			}
			if (details.currentTag) {
				$scope.editing.location.tags[details.currentTag] = true;
			};
		});
	};

	$scope.save = function() {
		var value;

		// This is a bit mucky but will do for now
		value = $scope.editing.location.date_of_admission;
		if (value) {
			$scope.editing.location.date_of_admission = moment(value, 'DD/MM/YYYY').format('YYYY-MM-DD');
		}

		value = $scope.editing.demographics.date_of_birth;
		if (value) {
			$scope.editing.demographics.date_of_birth = moment(value, 'DD/MM/YYYY').format('YYYY-MM-DD');
		}

		$http.post('patient/', $scope.editing).success(function(patient) {
			dialog.close(patient);
		});
	};

	$scope.cancel = function() {
		dialog.close('cancel');
	};
});

controllers.controller('EditItemCtrl', function($scope, $cookieStore, $timeout, dialog, item, options) {
	$scope.editing = item.makeCopy();
	$scope.editingName = item.patientName;
    $scope.currentTag = $cookieStore.get('opal.currentTag') || 'mine'; // initially display patients of interest to current user
    $scope.currentSubTag = 'all'; // initially display patients of interest to current user

    $scope.showSubtags = function(withsubtags){
        var show =  _.some(withsubtags, function(tag){ return $scope.editing.location.tags[tag] });
        return show
    };


	$timeout(function() {
		dialog.modalEl.find('input,textarea').first().focus();
	});

	for (var name in options) {
		if (name.indexOf('micro_test') != 0) {
			$scope[name + '_list'] = options[name];
		};
	};

	if (item.columnName == 'microbiology_test') {
		$scope.microbiology_test_list = [];
		$scope.microbiology_test_lookup = {};
        $scope.micro_test_defaults =  options.micro_test_defaults;

		for (var name in options) {
			if (name.indexOf('micro_test') == 0) {
				for (var ix = 0; ix < options[name].length; ix++) {
					$scope.microbiology_test_list.push(options[name][ix]);
					$scope.microbiology_test_lookup[options[name][ix]] = name;
				};
			};
		};

		$scope.$watch('editing.test', function(testName) {
			$scope.testType = $scope.microbiology_test_lookup[testName];
            if( _.isUndefined(testName) || _.isUndefined($scope.testType) ){
                return;
            }
            if($scope.testType in $scope.micro_test_defaults){
                _.each(_.pairs($scope.micro_test_defaults[$scope.testType]), function(values){
                    var field =  values[0];
                    var _default =  values[1];
                    $scope.editing[field] =  $scope.editing[field] ? $scope.editing[field] : _default;
                });
            }
		});
	};

	$scope.patient_category_list = ['Inpatient', 'Outpatient', 'Review'];

	$scope.save = function(result) {
		item.save($scope.editing).then(function() {
			dialog.close(result);
		});
	};

	$scope.cancel = function() {
		dialog.close('cancel');
	};
});

controllers.controller('DeleteItemConfirmationCtrl', function($scope, $http, $timeout, dialog, item) {
	$timeout(function() {
		dialog.modalEl.find('button.btn-primary').first().focus();
	});

	$scope.destroy = function() {
		item.destroy().then(function() {
			dialog.close('deleted');
		});
	};

	$scope.cancel = function() {
		dialog.close('cancel');
	};
});

controllers.controller('DischargePatientCtrl', function($scope, $http, $timeout, dialog, patient, currentTag) {
	$timeout(function() {
		dialog.modalEl.find('input,textarea').first().focus();
	});

	var currentCategory = patient.location[0].category;
	var newCategory;

	if (currentCategory == 'Inpatient') {
		newCategory = 'Discharged';
	} else if (currentCategory == 'Review' || currentCategory == 'Followup') {
		newCategory = 'Unfollow';
	} else {
		newCategory = currentCategory;
	}

	$scope.editing = {
		category: newCategory,
		//date: new Date()
	};

	$scope.discharge = function() {
		var location = patient.getItem('location', 0);
		var attrs = location.makeCopy();

		if ($scope.editing.category != 'Unfollow') {
			attrs.category = $scope.editing.category;
			attrs.discharge_date = $scope.editing.discharge_date;
		}

		if ($scope.editing.category != 'Followup') {
			attrs.tags[currentTag] = false;
		}

		location.save(attrs).then(function() {
			dialog.close('discharged');
		});
	};

	$scope.cancel = function() {
		dialog.close('cancel');
	};
});
