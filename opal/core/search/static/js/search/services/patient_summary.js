//
// This is the main PatientSummary class for OPAL.
//
angular.module('opal.services').factory('PatientSummary', function(UserProfile) {
        var PatientSummary = function(jsonResponse){
            var startYear, endYear;
            var self = this;

            if(jsonResponse.start_date){
                startYear= moment(jsonResponse.start_date, 'DD/MM/YYYY').format("YYYY");
            }

            if(jsonResponse.end_date){
                endYear = moment(jsonResponse.end_date, 'DD/MM/YYYY').format("YYYY");
            }

            if(startYear && endYear && startYear !== endYear){
              this.years = startYear + "-" + endYear;
            }
            else if(startYear){
                this.years = startYear;
            }
            this.first_name = jsonResponse.first_name;
            this.surname = jsonResponse.surname;
            this.patientId = jsonResponse.patient_id;
            this.count = jsonResponse.count;
            this.dateOfBirth = moment(jsonResponse.date_of_birth, 'DD/MM/YYYY');
            this.categories = jsonResponse.categories.join(", ");
            this.link = "/#/patient/" + jsonResponse.patient_id;
            this.hospitalNumber = jsonResponse.hospital_number;
            UserProfile.load().then(function(user_profile){
                self.canViewPatientNotes = _.contains(user_profile.roles.default, "micro_haem");
            })
        };

        return PatientSummary;
    });
