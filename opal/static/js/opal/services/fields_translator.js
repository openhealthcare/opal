angular.module('opal.services').service('FieldTranslator', function($rootScope){
  "use strict";
  /* this service provides translation to js, ie casting date fields and datetime
  * fields to moments
  */
  var self = this;
  var DATE_FORMAT = 'DD/MM/YYYY';
  var DATETIME_FORMAT = 'DD/MM/YYYY HH:mm:ss';


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


  this.translateFieldsToJs = function(fieldMapping, fieldValue){
      if(fieldMapping.type == 'date'){
          if(moment.isMoment(fieldValue)){
              return fieldValue;
          }
          if(_.isDate(fieldValue)){
            return moment(fieldValue);
          }
          return moment(fieldValue, DATE_FORMAT);
      }
      else if(fieldMapping.type == 'date_time'){
          if(moment.isMoment(fieldValue)){
              return fieldValue;
          }
          if(_.isDate(fieldValue)){
            return moment(fieldValue);
          }
          return moment(fieldValue, DATETIME_FORMAT);
      }

      return fieldValue;
  };

  this.subRecordToJs = function(subrecord, subrecordName){
    _.forEach(subrecord, function(fieldValue, fieldName){
        if(fieldValue){
            var fieldMapping = self.lookUpField(subrecordName, fieldName);
            if(fieldMapping){
              subrecord[fieldName] = self.translateFieldsToJs(fieldMapping, fieldValue);
            }
        }
    });

    return subrecord;
  }

  this.cleanString = function(fieldValue){
    if(angular.isString(fieldValue)){
      fieldValue = fieldValue.trim();

      if(!fieldValue){
          return undefined;
      }
    }

    return fieldValue;
  }

  this.translateJsToField = function(fieldMapping, fieldValue){
      if(fieldValue !== undefined && fieldValue !== null){
        if(fieldMapping.type === 'date'){
            if (!angular.isString(fieldValue)) {
                fieldValue = moment(fieldValue);
                fieldValue = fieldValue.format(DATE_FORMAT);
            }
            else{
                fieldValue = self.cleanString(fieldValue);
            }
        }
        else if(fieldMapping.type === 'date_time'){
          if(angular.isString(fieldValue)){
            fieldValue = self.cleanString(fieldValue);
          }
          else{
            fieldValue = moment(fieldValue).format(DATETIME_FORMAT);
          }
        }
        else if(fieldMapping.type == 'integer' || fieldMapping.type == 'float'){
          fieldValue = self.cleanString(fieldValue);
        }
      }
      return fieldValue;
  };

  this.jsToSubrecord = function(subrecordJs, subrecordName){
      _.forEach(subrecordJs, function(fieldValue, fieldName){
        var fieldMapping = self.lookUpField(subrecordName, fieldName);
        if(fieldMapping){
          subrecordJs[fieldName] = self.translateJsToField(fieldMapping, fieldValue);
        }
      });
      return subrecordJs;
  };

  this.itersingleSubrecords = function(patient, someFun){
    /*
    * iterates over subrecords of the form editing.demographics.firstname
    */
    _.forEach(patient, function(allSubrecords, subrecordName){
      someFun(allSubrecords, subrecordName);
    });
    return patient;
  };


  this.iterateSubrecords = function(patient, someFun){
    /*
    * iterates over subrecords of the form demographics: [{first_name: 'Sue'}]
    */
    _.forEach(patient, function(allSubrecords, subrecordName){
      _.forEach(allSubrecords, function(subrecordFields){
        someFun(subrecordFields, subrecordName);
      });
    });
    return patient;
  };

  this.jsToPatient = function(originalPatient){
      var patient = self.itersingleSubrecords(originalPatient, self.jsToSubrecord);
      delete patient.merged;
      return patient;
  };

  this.patientToJs = function(originalPatient){
    var patient = self.iterateSubrecords(originalPatient, self.subRecordToJs);
    return patient;
  };
});
