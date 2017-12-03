angular.module('opal.controllers').controller(
  "DefaultSingleStep", function(scope, step, episode){
    if(scope.editing[step.model_api_name]){
      scope.editing[step.model_api_name] = _.last(scope.editing[step.model_api_name]);
    }
    else if(episode){
      scope.editing[step.model_api_name] = episode.newItem(step.model_api_name);
    }
    else{
      // TODO change this when we support subrecord creation without an episode
      scope.editing[step.model_api_name] = {};
    }
  }
);
