angular.module('opal.services').service('Patient', function(Episode, FieldTranslater) {
  "use strict";
  var Patient = function(patientData){
    var self = this;
    _.extend(this, FieldTranslater.patientToJs(patientData));
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

    var episodeValues = _.values(patientData.episodes);
    if(episodeValues.length){
      _.each(this, function(v, k){
          if(k in episodeValues[0]){
              self[k] = episodeValues[0][k];
          }
      });
      this.recordEditor = episodeValues[0].recordEditor;
    }
  };

  return Patient;
});
