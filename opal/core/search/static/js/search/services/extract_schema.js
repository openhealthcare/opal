angular.module('opal.services').factory('ExtractSchema', function(Schema) {
  "use strict";

  var NOT_ADVANCED_SEARCHABLE = [
      "created", "updated", "created_by_id", "updated_by_id"
  ];

  var ExtractSchema = function(columns){
    columns = _.each(columns, function(column){
      column.fields = this.getAdvancedSearchFields(column);
    }, this);

    Schema.call(this, columns);
  };

  ExtractSchema.prototype = angular.copy(Schema.prototype);

  var additionalPrototype= {
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
  }
  _.extend(ExtractSchema.prototype, additionalPrototype);

  return ExtractSchema
});
