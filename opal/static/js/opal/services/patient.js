angular.module('opal.services').service('Patient', function(Episode, FieldTranslator) {
  "use strict";
  var Patient = function(patientData){
    var self = this;
    _.extend(this, FieldTranslator.patientToJs(patientData));
    this.episodes = _.map(this.episodes, function(resource) {
      return new Episode(resource);
    });
    this.episodes = _.sortBy(this.episodes, function(episode){
      /*
      * so we cast to unix because if an event hasn't got
      * a start or an end, we want it at the bottom
      */
      if(episode.end){
        return moment(episode.end).unix();
      }
      else if(episode.start){
        return moment(episode.start).unix();
      }
      else{
          return 0;
      }
    }).reverse();


    // TODO: There are edge cases here - e.g. We are viewing Episode 3,
    // which has a custom detail view which only displays some elements
    // based on demographics - e.g. "only display the parental consent
    // details if the patient is under 18". This won't have access to
    // changed Demographics if we change them.

    // We're replacing any patient subrecords with a reference to the
    // EditItem requires an episode to work with.
    var episodeValues = _.values(this.episodes);
    if(episodeValues.length){
      _.each(this, function(v, k){
          if(k in episodeValues[0]){
            if(k !== "id"){
              self[k] = episodeValues[0][k];
            }
          }
      });
      this.recordEditor = episodeValues[0].recordEditor;
    }
  };

  return Patient;
});
