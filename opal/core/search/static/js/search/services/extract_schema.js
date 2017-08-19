angular.module('opal.services').factory('ExtractSchema', function() {
  var ExtractSchema = function(columns){
    this.columns = this.getAdvancedSearchColumns(columns);

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
      columns = angular.copy(c);
      return _.filter(columns, function(c){
        return c.advanced_searchable
      });
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
