angular.module('opal.services').factory('EditingEpisode', function($rootScope){
    "use strict";

    /*
    * The Editing Episode is the name of the object that sits
    * on scope as 'editing'
    *
    * this is what an episode is serialised to
    */

    var EditingHelper = function(parent, episode){
        this.parent = parent;
        this.episode = episode;
    };

    EditingHelper.prototype = {
      remove: function(modelApiName, index){
        this.parent[modelApiName].splice(index, 1);
      },
      isRecordFilledIn: function(subrecord){
        var subrecordKeys = _.keys(subrecord);
        return !!_.filter(subrecordKeys, function(k){
          if(k == "_client" || k.indexOf("$") == 0){
          return false;
          }
          if(_.isString(subrecord[k]) && !subrecord[k].length){
           return false;
          }
          return true;
        }).length;
      },
      addRecord: function(modelApiName){
        if(!this.parent[modelApiName]){
          this.parent[modelApiName] = [];
        }

        if(this.episode){
          var newItem = this.episode.newItem(modelApiName);
          this.parent[modelApiName].push(newItem.makeCopy());
        }
        else{
          this.parent[modelApiName].push(this.getNewRecord(modelApiName));
        }
      },
      getNewRecord: function(modelApiName){
        return {
          _client: {
            completed: false,
            id: _.uniqueId(modelApiName)
          }
        }
      },
      update: function(patient){
        var parent = this.parent;
        _.each($rootScope.fields, function(value, key){
          delete parent[key];
          var copies = _.map(
            episode[key],
            function(record){
              return record.makeCopy();
          });
          if(value.single){
            parent[key] = copies[0];
          }
          else{
            parent[key] = copies;
          }
        });
      }
    };

    var EditingEpisode = function(episode){
      this.helper = new EditingHelper(this, episode);
      var self = this;
      if(episode){
        this.helper.update(episode)
      }
    };

    return EditingEpisode;
});
