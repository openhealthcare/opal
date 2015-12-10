//
// This is the main PatientSummary class for OPAL.
//
angular.module('opal.services').factory('PatientSummary', function(UserProfile) {
        var PatientSummary = function(jsonResponse){
            var startYear, endYear;
            var DATE_FORMAT = "DD/MM/YYYY"
            var self = this;

            if(jsonResponse.start_date && jsonResponse.end_date){
                if(jsonResponse.start_year){
                    startYear= moment(jsonResponse.start_date, DATE_FORMAT).format("YYYY");
                }

                if(jsonResponse.end_date){
                    endYear = moment(jsonResponse.end_date, DATE_FORMAT).format("YYYY");
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
            this.dateOfBirth = moment(jsonResponse.date_of_birth, DATE_FORMAT);
            this.categories = jsonResponse.categories.join(", ");
            this.link = "#/episode/" + jsonResponse.episode_id;
            this.patientNotesLink = "#/patient/" + jsonResponse.id;
            this.canViewPatientNotes = false;
            this.hospitalNumber = jsonResponse.hospital_number;
            UserProfile.then(function(user_profile){
                self.canViewPatientNotes = _.contains(user_profile.roles.default, "micro_haem");
            })
        };

        return PatientSummary;
    });
