angular.module('opal.services').factory('ExtractSchema', function() {
  var ExtractSchema = function(columns){
    this.columns = columns;

    // set up a reference from the field to the subrecord
    _.each(this.columns, function(c){
      _.each(c.fields, function(f){
        if(f.subrecord){
          throw Exception(
            'the subrecord field has been declared on a namespace we need'
          )
        }
        f.subrecord = c;
      });
    });
  }

  ExtractSchema.prototype = {
    getColumn: function(columnName){
      var result = _.find(columns, function(c){
          return c.name === columnName
      })

      if(result){
          return result;
      }

      throw new Error('No such column with name: "' + columnName + '"');
    },
    isSingleton: function(columnName){
      var column = this.getColumn(columnName);
      return column.single;
    },
    isReadOnly: function(columnName){
      var column = this.getColumn(columnName);
      return column.readOnly;
    },
    getAdvancedSearchColumns: function(){
        return _.filter(this.columns, function(c){
            return c.advanced_searchable
        })
    }
  }

  return ExtractSchema
});
