angular.module('opal.services')
    .factory('episodeVisibility', function(){
    return function(episode, $scope) {

        var location = episode.location[0];
        var demographics = episode.demographics[0];
        var hospital_number = $scope.query.hospital_number;
        var name = $scope.query.name;
        var ward = $scope.query.ward;
        var bed = $scope.query.bed;

        // Not active (no tags) - hide it.
        if(!episode.active && $scope.currentTag != 'mine'){
            return false;
        }

        // Not in the top level tag - hide it
	    if (_.keys(episode.tagging[0]).indexOf($scope.currentTag) == -1 ||
            !episode.tagging[0][$scope.currentTag]) {
		    return false;
	    }

        // Not in the current subtag
	    if ($scope.currentSubTag != 'all' &&
            (_.keys(episode.tagging[0]).indexOf($scope.currentSubTag) == -1 ||
             !episode.tagging[0][$scope.currentSubTag])){
		    return false;
	    }

        // filtered out by hospital number
        if (demographics.hospital_number &&
            demographics.hospital_number.toLowerCase().indexOf(
                hospital_number.toLowerCase()) == -1) {
		    return false;
	    }

        // Filtered out by name.
        if (name &&  demographics.name && // Was it passed in?
            demographics.name.toLowerCase().indexOf(name.toLowerCase()) == -1) {
		    return false;
	    }


        // Filtered out by ward.
        if (ward &&  // Was it passed in?
            location.ward.toLowerCase().indexOf(ward.toLowerCase()) == -1) {
		    return false;
	    }

        if(bed){
            if(bed.indexOf('-') == -1 ){
                return location.bed == bed
            }else{
                var pair = bed.split('-')
                var frist = pair[0];
                var last = pair[1]
                if( location.bed <= last && location.bed >= frist){
                    return true
                }
                return false;
            }
        }

        return true;
	}
});
