var option_lists = [
	'antimicrobial',
	'antimicrobial_route',
	'condition',
	'destination',
	'microbiology_organism',
	'patient_category',
	'travel_reason',
];

var microbiology_test_list = [
	'Broncheoalveolar lavage MC&S',
	'Blood Culture',
	'CSF AFB microscopy & TB culture',
	'CSF MC&S',
	'Fluid MC&S',
	'Lymph Node MC&S',
	'Pleural MC&S',
	'Sputum AFB microscopy & TB culture',
	'Sputum MC&S',
	'Stool MC&S',
	'Stool OCP',
	'Throat Swab MC&S',
	'Tissue AFB microscopy & TB culture',
	'Tissue MC&S',
	'Urine AFB microscopy & TB culture',
	'Urine MC&S',
	'Wound swab MC&S',
	'CMV Serology',
	'Dengue Serology',
	'Hepatitis A Serology',
	'Hepatitis E Serology',
	'Measles Serology',
	'Rubella Serology',
	'Toxoplasmosis Serology',
	'VZV Serology',
	'Brucella Serology',
	'EBV Serology',
	'HIV',
	'Hepatitis B Serology',
	'Syphilis Serology',
	'Cryptococcal antigen',
	'Dengue PCR',
	'JC Virus PCR',
	'MRSA PCR',
	'Rickettsia PCR',
	'Scrub Typhus PCR',
	'Borrleia Screening Serology',
	'Brorleia Reference Serology',
	'Viral Haemorrhagic Fever PCR',
	'Amoebic Serology',
	'Cystercicosis Serology',
	'Fasciola Serology',
	'Filaria Serology',
	'Hydatid Serology',
	'Strongyloides Serology',
	'Toxcocara Serology',
	'Trypanosomiasis brucei Serology',
	'Trypanosomiasis cruzi serology',
	'Hepatitis C Serology',
	'Hepatitis D Serology',
	'HHV-6 Serology',
	'HHV-7 Serology',
	'HTLV Serology',
	'CMV Viral Load',
	'EBV Viral Load ',
	'HBV Viral Load',
	'HCV Viral Load',
	'HHV-6 Viral Load',
	'HHV-7 Viral Load',
	'HHV-8 Viral Load',
	'HIV Viral Load',
	'Measles PCR',
	'VZV Viral Load',
	'Babesia Film',
	'Malaria Film',
	'Microfilarial Film',
	'Swab PCR',
	'C. difficile',
	'Leishmaniasis PCR',
	'CSF PCR',
	'Respiratory Virus PCR',
	'Stool PCR',
	'Stool Parasitology PCR',
	'Other',
];

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


	$http.get('schema/').success(function(columns) {
		$scope.columns = columns;

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
	})

	$scope.getCix = function(name) {
		for (var cix = 0; cix < $scope.columns.length; cix++) {
			if ($scope.columns[cix].name == name) {
				return cix;
			}
		}
		throw 'Unexpected column name: ' + name
	};


	for (var i = 0; i < option_lists.length; i++) {
		(function(option) {
			$http.get('options/' + option + '_list/').success(function(data) {
				$scope[option + '_list'] = [];
				$scope[option + '_synonyms'] = {};
				for (var j = 0; j < data.length; j++) {
					$scope[option + '_list'].push(data[j][0]);
					$scope[option + '_synonyms'][data[j][0]] = data[j][1];
				};
			});
		})(option_lists[i]);
	}


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
		var column = $scope.columns[cix];

		$scope.rows[rix][column.name].splice(iix, 1);
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
