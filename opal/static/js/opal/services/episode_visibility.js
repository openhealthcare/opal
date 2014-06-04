angular.module('opal.services')
    .factory('episodeVisibility', function(){
    return function(episode, $scope, viewDischarged) {

        var location = episode.location[0];
        var demographics = episode.demographics[0];
        var hospital_number = $scope.query.hospital_number;
        var name = $scope.query.name;

        // Not active (no tags) - hide it.
        if(!episode.active && $scope.currentTag != 'mine' && !viewDischarged){
            return false;
        }

        // Not in the top level tag - hide it
	    if (episode.tagging[$scope.currentTag] != true) {
		    return false;
	    }

        // Not in the current subtag
	    if ($scope.currentSubTag != 'all' &&
            episode.tagging[$scope.currentSubTag] != true){
		    return false;
	    }

        // filtered out by hospital number
	    if (demographics.hospital_number &&
            demographics.hospital_number.toLowerCase().indexOf(
                hospital_number.toLowerCase()) == -1) {
		    return false;
	    }

        // Filtered out by name.
        if (demographics.name.toLowerCase().indexOf(name.toLowerCase()) == -1) {
		    return false;
	    }
        return true;
	}
});
