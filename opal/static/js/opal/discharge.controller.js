controllers.controller('DischargeEpisodeCtrl', function($scope, $timeout,
                                                        dialog, episode, currentTag) {
	$timeout(function() {
		dialog.modalEl.find('input,textarea').first().focus();
	});

	var currentCategory = episode.location[0].category;
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

    $scope.episode = episode.makeCopy();
    $scope.episode.discharge_date = moment().format('DD/MM/YYYY');

	$scope.discharge = function() {
		var location = episode.getItem('location', 0);
		var attrs = location.makeCopy();

		if ($scope.editing.category != 'Unfollow') {
			attrs.category = $scope.editing.category;
		}

		if ($scope.editing.category != 'Followup') {
			attrs.tags[currentTag] = false;
		}

		location.save(attrs).then(function() {
            // TODO: Don't hard code workflow in OPAL.
            if($scope.editing.category!= 'Followup'){
                $scope.episode.active = false;
            }
            episode.save($scope.episode).then(function(){
			    dialog.close('discharged');
            });
		});
	};

	$scope.cancel = function() {
		dialog.close('cancel');
	};
});
