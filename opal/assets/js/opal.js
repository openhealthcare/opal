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
	var editing = false;
	var deleting = false;

	$scope.rows = [];

	$scope.rix = 0; // row index
	$scope.cix = 0; // column index
	$scope.iix = 0; // item index

	$scope.mouseRix = -1; // index of row mouse is currently over
	$scope.mouseCix = -1; // index of column mouse is currently over

	$http.get('assets/records.json').success(function(rows) {
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
		{name: 'antimicrobials', title: 'Antimicrobials', multi: true},
		{name: 'microbiology', title: 'Microbiology Results', multi: true},
		{name: 'microbiologyComments', title: 'Microbiology Input', multi: true},
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

	var option_lists = [
		'antimicrobial',
		'antimicrobial_route',
		'condition',
		'destination',
		'microbiology_organism',
		'patient_category',
		'travel_reason',
	];

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

	$scope.microbiology_test_list = [
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
		if ($scope.columns[cix]['multi']) {
			$scope.editing = clone($scope.rows[rix][columnName][iix]);
		} else {
			$scope.editing = clone($scope.rows[rix][columnName]);
		}
		$('#' + columnName + '-modal').modal();
		$('#' + columnName + '-modal').find('input,textarea').first().focus();
	};

	function startDelete() {
		var rix = $scope.rix;
		var cix = $scope.cix;
		var iix = $scope.iix;
		var column = $scope.columns[cix];

		if (!column.multi) {
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

		for (var cix = 0; cix < $scope.columns.length; cix++) {
			column = $scope.columns[cix];
			if (column.multi) {
				newRecord[column.name] = [{}];
			}
		}

		$scope.rows.push(newRecord);
		$scope.selectItem($scope.rows.length - 1, 0, 0);
		startEdit();
	};

	$scope.saveEdit = function() {
		var rix = $scope.rix;
		var cix = $scope.cix;
		var iix = $scope.iix;
		var columnName = $scope.columns[cix].name;

		clearModal(columnName);
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
			return 'assets/templates/' + tAttrs.column + '.html'
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
			return 'assets/templates/' + tAttrs.column + '-modal.html'
		},
	}
});
