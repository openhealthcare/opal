//
// This is the main PatientSummary class for OPAL.
//
angular.module('opal.services').factory('PatientSummary', function() {
    "use strict";
    var PatientSummary = function(jsonResponse){
        this.data = jsonResponse;
        var startYear, endYear

        if(jsonResponse.start_date){
            this.startDate = moment(jsonResponse.start_date, 'DD/MM/YYYY');
            startYear= this.startDate.format("YYYY");
        }

        if(jsonResponse.end_date){
            this.endDate = moment(jsonResponse.end_date, 'DD/MM/YYYY');
            endYear = this.endDate.format("YYYY");
        }

        if(startYear && endYear && startYear !== endYear){
            this.years = startYear + "-" + endYear;
        }
        else if(startYear){
            this.years = startYear;
        }

        if(jsonResponse.date_of_birth){
            this.dateOfBirth = moment(jsonResponse.date_of_birth, 'DD/MM/YYYY');
        }

        if(jsonResponse.patient_id){
            this.link = "/#/patient/" + jsonResponse.patient_id;
            this.patientId = jsonResponse.patient_id;
        }

        if(jsonResponse.categories){
            this.categories = jsonResponse.categories.join(", ");
        }

        this.first_name = jsonResponse.first_name;
        this.surname = jsonResponse.surname;
        this.count = jsonResponse.count;
        this.dateOfBirth = moment(jsonResponse.date_of_birth, 'DD/MM/YYYY');
        this.hospitalNumber = jsonResponse.hospital_number;
    };

    return PatientSummary;
});
