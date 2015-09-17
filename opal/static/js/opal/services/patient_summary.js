//
// This is the main PatientSummary class for OPAL.
//
angular.module('opal.services').factory('PatientSummary', function() {
        var PatientSummary = function(jsonResponse){
            var startYear, endYear;

            if(jsonResponse.start_date && jsonResponse.end_date){
                if(jsonResponse.start_year){
                    startYear= moment(jsonResponse.start_date, 'YYYY-MM-DD').format("YYYY");
                }

                if(jsonResponse.end_date){
                    endYear = moment(jsonResponse.end_date, 'YYYY-MM-DD').format("YYYY");
                }
            }

            if(startYear && endYear && startYear !== endYear){
                this.years = startYear + "-" + endYear;
            }
            else if(startYear){
                this.years = startYear;
            }
            this.name = jsonResponse.name;
            this.count = jsonResponse.count;
            this.dateOfBirth = moment(jsonResponse.date_of_birth, 'YYYY-MM-DD');
            this.categories = jsonResponse.categories.join(", ");
            this.link = "#/episode/" + jsonResponse.episode_id;
            this.hospitalNumber = jsonResponse.hospital_number;
        };

        return PatientSummary;
    });
