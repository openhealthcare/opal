angular.module('opal.services').service('Pathway', function(
    $http, FieldTranslator, $q, $window, $rootScope
){
    "use strict";
    var Pathway = function(pathwayDefinition, episode){
      this.save_url = pathwayDefinition.save_url;
      this.steps = pathwayDefinition.steps;
      this.display_name = pathwayDefinition.display_name;
      this.icon = pathwayDefinition.icon;
      this.finish_button_text = pathwayDefinition.finish_button_text;
      this.finish_button_icon = pathwayDefinition.finish_button_icon;
      this.pathwayResult = $q.defer();
      this.pathwayPromise = this.pathwayResult.promise;
      this.episode = episode;
    };

    Pathway.prototype = {
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
            if(value.single){
              editing[key] = copies[0];
            }
            else{
              editing[key] = copies;
            }
          });
        }

        return editing;
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
                return FieldTranslator.jsToSubrecord(x, key);
              });
            }
            else{
              delete val._client;
              result = [FieldTranslator.jsToSubrecord(val, key)];
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
