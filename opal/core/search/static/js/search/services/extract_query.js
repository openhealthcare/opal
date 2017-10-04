angular.module('opal.services').factory('ExtractQuery', function(){
  var baseModel = {
    column     : null,
    field      : null,
    queryType  : null,
    query      : null
  };

  var ExtractQuery = function(schema){
    // the seatch query
    this.criteria = [_.clone(baseModel)];
    this.combinations = ["all", "any"];
    this.requiredExtractFieldNames = [
      ['demographics', 'date_of_birth'],
      ['demographics', 'sex'],
    ]
    this.requiredExtractFields = [];
    _.each(this.requiredExtractFieldNames, function(subrecordAndFieldName){
      this.requiredExtractFields.push(
        schema.findField(subrecordAndFieldName[0], subrecordAndFieldName[1])
      );
    }, this);

    // whether the user would like an 'or' conjunction or and 'and'
    this.anyOrAll = this.combinations[0];

    // the columns in the download
    // shallow copies ftw
    this.slices = _.clone(this.requiredExtractFields);
  };

  ExtractQuery.prototype = {
    addSlice: function(someField){
      // add a field to the extract fields
      if(!this.isSliceAdded(someField)){
        this.slices.push(someField);
      }
    },
    isSubrecordAdded: function(someSubrecord){
      return someSubrecord.fields.length === _.filter(this.slices, function(field){
        return field.subrecord === someSubrecord;
      }).length;
    },
    isSliceAdded: function(someField){
      return _.indexOf(this.slices, someField) !== -1
    },
    addSubrecordSlices: function(someSubrecord){
      // adds all fields for a subrecord
      _.each(someSubrecord.fields, this.addSlice, this);
    },
    removeSubrecordSlices: function(someSubrecord){
      // adds all fields for a subrecord
      _.each(someSubrecord.fields, this.removeSlice, this);
    },
    removeSlice: function(someField){
      // remove a field from the extract fields
      this.slices = _.filter(this.slices, function(slicedField){
        return someField !== slicedField || this.sliceIsRequired(slicedField);
      }, this);
    },
    sliceIsRequired: function(someField){
      return _.indexOf(this.requiredExtractFields, someField) !== -1;
    },
    getDataSlices: function(){
      var result = {}
      _.each(this.slices, function(field){
        if(!(field.subrecord.name in result)){
          result[field.subrecord.name] = [];
        }
        result[field.subrecord.name].push(
          field.name
        );
      });
      return result;
    },
    readableQueryType: function(someQuery){
      if(!someQuery){
        return someQuery;
      }
      var result = someQuery;
      if(someQuery === "Equals"){
        result = "is";
      }
      if(someQuery === "Before" || someQuery === "After"){
        result = "is " + result;
      }
      if(someQuery === "All Of" || someQuery === "Any Of"){
        result = "is"
      }

      return result.toLowerCase();
    },

    completeCriteria: function(){
      var combine;
      // queries can look at either all of the options, or any of them
      // ie 'and' conjunctions or 'or'
      if(this.anyOrAll === 'all'){
        combine = "and";
      }
      else{
        combine = 'or';
      }

      // remove incomplete criteria
      criteria = _.filter(this.criteria, function(c){
          // Ensure we have a query otherwise
          if(c.column &&  c.field &&  c.queryType && c.query){
              return true;
          }
          c.combine = combine;
          // If not, we ignore this clause
          return false;
      });

      _.each(criteria, function(c){
        c.combine = combine;
      });

      return criteria
    },
    addFilter: function(){
        this.criteria.push(_.clone(baseModel));
    },
    removeFilter: function(index){
        if(this.selectedInfo === this.criteria[index]){
          this.selectedInfo = undefined;
        }
        if(this.criteria.length == 1){
            this.removeCriteria();
        }
        else{
            this.criteria.splice(index, 1);
        }
    },
    resetFilter: function(queryRow, fieldsTypes){
      // when we change the column, reset the rest of the query
      _.each(queryRow, function(v, k){
        if(!_.contains(fieldsTypes, k) && k in baseModel){
          queryRow[k] = baseModel[k];
        }
      });
    },
    removeCriteria: function(){
        this.criteria = [_.clone(baseModel)];
    }
  }

  return ExtractQuery;
});
