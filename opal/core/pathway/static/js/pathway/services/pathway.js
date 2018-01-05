angular.module('opal.services').service('Pathway', function(
    $http, FieldTranslater, $q, $controller, $window, $rootScope
){
    "use strict";
    var Pathway = function(pathwayDefinition, episode){
      this.save_url = pathwayDefinition.save_url;
      this.steps = angular.copy(pathwayDefinition.steps);
      this.display_name = pathwayDefinition.display_name;
      this.icon = pathwayDefinition.icon;
      this.finish_button_text = pathwayDefinition.finish_button_text;
      this.finish_button_icon = pathwayDefinition.finish_button_icon;
      this.pathwayResult = $q.defer();
      this.pathwayPromise = this.pathwayResult.promise;
      this.episode = episode;
    };

    Pathway.prototype = {
      remove: function(editing, modelApiName, index){
        // removes an element from the editing dictionary
        editing[modelApiName].splice(index, 1);
      },
      getNewRecord: function(modelApiName){
        // this is used to create a completely clean subrecord
        // if an episode does not exist
        return {
          _client: {
            completed: false,
            id: _.uniqueId(modelApiName)
          }
        }
      },
      addRecord: function(editing, modelApiName){
        // adds a record to the editing object
        if(!editing[modelApiName]){
          editing[modelApiName] = [];
        }

        if(this.episode){
          var newItem = this.episode.newItem(modelApiName);
          editing[modelApiName].push(newItem.makeCopy());
        }
        else{
          editing[modelApiName].push(this.getNewRecord(modelApiName));
        }
      },
      isRecordFilledIn: function(subrecord){
        // validates if a subrecord has been populated
        var subrecordKeys = _.keys(subrecord);
        return !!_.filter(subrecordKeys, function(k){
          if(k == "_client" || k.indexOf("$") == 0){
            return false;
          }
          if(_.isString(subrecord[k]) || _.isArray(subrecord[k])){
            return subrecord[k].length
          }
          else{
            return subrecord[k];
          }
          return false;
        }).length;
      },
      register: function(apiName, stepScope){
        var step = _.findWhere(this.steps, {api_name: apiName});
        step.scope = stepScope;
      },
      populateEditingDict: function(episode){
        var editing = {};
        if(episode){
          var self = this;
          _.each($rootScope.fields, function(value, key){
            var copies = _.map(
              episode[key],
              function(record){
                return record.makeCopy();
            });
            editing[key] = copies;
          });
        }

        return editing;
      },
      updatePatientEditing: function(editing, patient){
        // updates the editing dictionary. It doesn't delete
        // existing as these could have been made by previous steps
        // it assumes what it is passed is a Patient object
        var newEditing = this.populateEditingDict(patient);
        _.each(newEditing, function(value, key){
          if(key !== "episodes"){
            editing[key] = value;
          }
        });
      },
      cancel: function(){
        this.pathwayResult.resolve();
      },
      compactEditing: function(editing){
        /*
        * looks for subrecords that are appearing as nulls and removes them
        */

        // remove all nulls that are in arrays
        var compactEditing = _.mapObject(editing, function(v, k){
          if(_.isArray(v)){
            return _.compact(v);
          }
          return v
        });

        // if we have empty objects or empty arrays, remove them
        compactEditing= _.omit(compactEditing, function(v, k, o){
          if(_.isArray(v)){
            return !v.length;
          }
          else{
            return !v;
          }
        });

        return compactEditing;
      },
      preSave: function(editing){},
      valid: function(editing){ return true; },
      finish: function(editing){
          var self = this;
          editing = angular.copy(editing);

          _.each(self.steps, function(step){
              if(step.scope.preSave){
                  step.scope.preSave(editing);
              }
          });

          var compactedEditing = self.compactEditing(editing);

          // cast the item to the fields for the server
          var toSave = _.mapObject(compactedEditing, function(val, key){
            var result;
            if(_.isArray(val)){
              result = _.map(val, function(x){
                delete x._client;
                return FieldTranslater.jsToSubrecord(x, key);
              });
            }
            else{
              delete val._client;
              result = [FieldTranslater.jsToSubrecord(val, key)];
            }
            return _.filter(result, function(subrecord){
                return _.size(subrecord);
            });
          });
          var endpoint = this.save_url;
          var result = $http.post(endpoint, toSave).then(
             function(response){
                self.pathwayResult.resolve(response.data);
           }, function(error){
               $window.alert("unable to save patient");
           });
           return result;
      }
    };

    return Pathway;
});
