angular.module('opal.services').factory('ExtractSchema', function() {
  "use strict";

  var NOT_ADVANCED_SEARCHABLE = [
      "created", "updated", "created_by_id", "updated_by_id"
  ];

  var ExtractSchema = function(columns){
    this.columns = this.getAdvancedSearchColumns(columns);
    _.each(this.columns, function(column){
      column.fields = this.getAdvancedSearchFields(column);
    }, this);

    // set up a reference from the field to the subrecord
    _.each(this.columns, function(c){
      _.each(c.fields, function(f){
        if(f.subrecord){
          throw 'the subrecord field has been declared on a namespace we need'
        }
        f.subrecord = c;
      });
    });
  };


  ExtractSchema.prototype = {
    getAdvancedSearchColumns: function(c){
      var columns = angular.copy(c);
      return _.filter(columns, function(c){
        return c.advanced_searchable
      });
    },
    getAdvancedSearchFields: function(column){
      if(column.name == 'microbiology_test' || column.name == 'investigation'){
        var micro_fields = [
          "test",
          "date_ordered",
          "details",
          "microscopy",
          "organism",
          "sensitive_antibiotics",
          "resistant_antibiotics"
        ];

        return _.filter(column.fields, function(field){
            return _.contains(micro_fields, field.name)
        })
      }
      return _.map(
          _.reject(
              column.fields,
              function(c){
                  if(_.contains(NOT_ADVANCED_SEARCHABLE, c.name)){
                      return true;
                  }
                  return c.type == 'token' ||  c.type ==  'list';
              }),
          function(c){ return c; }
      ).sort()
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
    }
  }

  return ExtractSchema
});
