angular.module('opal.services').factory('Schema', function() {
    "use strict";
    var Schema = function(columns){
      this.columns = angular.copy(columns);
      this.chunkedColumns = this.chunkColumns(columns);
      _.each(this.columns, function(c){
        _.each(c.fields, function(f){
          if(f.subrecord){
            throw 'the subrecord field has been declared on a namespace we need'
          }
          f.subrecord = c;
        });
      });
    };

    Schema.prototype = {
      chunkColumns: function(columns){
        /*
        * chunks the columns into groups of 6 so that
        * they can be displayed in vertical columns
        */
        var chunkAmount = 6;
        return _.values(_.groupBy(columns, function(element, index){
          return Math.floor(index/chunkAmount);
        }));
      },
      findColumn: function(columnName){
        if(!columnName){
          return;
        }
        return _.findWhere(this.columns, {name: columnName});
      },
      findField: function(columnName, fieldName){
        /*
        * returns the field object from the schema when given column.name and field.name
        */
        var column = this.findColumn(columnName);
        if(!column){return;}
        return _.findWhere(
            column.fields, {name: fieldName}
        );
      },
      isType: function(columnName, field, type){
        var theField = this.findField(columnName, field);
        if(!columnName || !field){
            return false;
        }
        if(!theField){ return false; }
        if (_.isArray(type)){
            var match = false;
            _.each(type, function(t){ if(t == theField.type){ match = true; } });
            return match;
        }else{
            return theField.type == type;
        }
      },
      isBoolean: function(columnName, field){
          return this.isType(columnName, field, ["boolean", "null_boolean"]);
      },
      isText: function(columnName, field){
          return this.isType(columnName, field, "string") || this.isType(columnName, field, "text");
      },
      isSelect: function(columnName, field){
          return this.isType(columnName, field, "many_to_many");
      },
      isSelectMany: function(columnName, field){
          return this.isType(columnName, field, "many_to_many_multi_select");
      },
      isDate: function(columnName, field){
          return this.isType(columnName, field, "date");
      },
      isDateTime: function(columnName, field){
          return this.isType(columnName, field, "date_time");
      },
      isDateType: function(columnName, field){
          // if the field is a date or a date time
          return this.isDate(columnName, field) || this.isDateTime(columnName, field);
      },
      isNumber: function(columnName, field){
          return this.isType(columnName, field, ["float", "big_integer", "integer", "positive_integer_field", "decimal"]);
      },
      getTypeDisplay: function(columnName, field){
        var field = this.findField(columnName, field);

        if(field){
          return field.type_display_name
        }
      },
      getChoices: function(column, field, referencedata){
        var modelField = this.findField(column, field);

        if(modelField.lookup_list && modelField.lookup_list.length){
          return referencedata.get(modelField.lookup_list);
        }

        if(modelField.enum){
          return modelField.enum;
        }
      }
    }

    return Schema
});
