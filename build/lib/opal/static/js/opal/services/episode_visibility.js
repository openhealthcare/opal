//
// This service allows us to dynamically filter visible episodes.
// (This is particularly useful in e.g. a patient list with many patients)
//
// In the current implementation there are a small number of allowed filters
//
// * Name
// * Hospital Number
// * Ward
// * Bed
//
// TODO: At some point in the future we might like to refactor this to be
// significantly more generic, or indeed consider whether it makes any real
// sense to have this fuctionality in it's own service rather than in the
// Patient List controller.
//
angular.module('opal.services')
    .factory('episodeVisibility', function(){
    return function(episode, $scope) {

        var location = episode.location[0];
        var demographics = episode.demographics[0];
        var hospital_number = $scope.query.hospital_number;
        var name = $scope.query.name;
        var ward = $scope.query.ward;
        var bed = $scope.query.bed;
        var patient_name = demographics.first_name + ' ' + demographics.surname;

        // filtered out by hospital number
        if (demographics.hospital_number &&
            demographics.hospital_number.toLowerCase().indexOf(
                hospital_number.toLowerCase()) == -1) {
		    return false;
	    }

        // Filtered out by name.
        if (name &&  patient_name && // Was it passed in?
            patient_name.toLowerCase().indexOf(name.toLowerCase()) == -1) {
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
