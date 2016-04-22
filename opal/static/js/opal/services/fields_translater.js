angular.module('opal.services').service('FieldTranslater', function($rootScope){
  "use strict";
  /* this service provides translation to js, ie casting date fields and datetime
  * fields to moments
  */
  var self = this;
  var DATE_FORMAT = 'DD/MM/YYYY';


  this.lookUpField = function(subrecordName, fieldName){
      var fieldBySubrecord = $rootScope.fields[subrecordName];
      if(!fieldBySubrecord){
          return;
      }
      var allFields = fieldBySubrecord.fields;
      return _.find(allFields, function(x){
          return x.name == fieldName;
      });
  };


  this.patientToJs = function(originalPatient){
    var patient = angular.copy(originalPatient);
    _.forEach(patient, function(allSubrecords, subrecordName){
      _.forEach(allSubrecords, function(subrecordFields){
        _.forEach(subrecordFields, function(fieldValue, fieldName){
            if(fieldValue){
                var fieldMapping = self.lookUpField(subrecordName, fieldName);
                if(fieldMapping){
                  if(fieldMapping.type == 'date'){
                      subrecordFields[fieldName] = moment(fieldValue, DATE_FORMAT);
                  }
                  else if(fieldMapping.type == 'date_time'){
                      subrecordFields[fieldName] = moment(fieldValue, DATE_FORMAT);
                  }
                }
            }
        });
      });
    });

    if(patient.merged && patient.merged.length){
        patient.merged = [self.patientToJs(patient.merged[0])];
    }

    return patient;
  };
});
