angular.module('opal.services').factory('ExtractSchema', function() {
  var ExtractSchema = function(columns){
    this.columns = angular.copy(columns);

    // set up a reference from the field to the subrecord
    _.each(this.columns, function(c){
      _.each(c.fields, function(f){
        if(f.subrecord){
          throw 'the subrecord field has been declared on a namespace we need'
        }
        f.subrecord = c;
      });
    });
  }

  ExtractSchema.prototype = {
    getAdvancedSearchColumns: function(){
        return _.filter(this.columns, function(c){
            return c.advanced_searchable
        })
    }
  }

  return ExtractSchema
});
