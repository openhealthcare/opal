angular.module('opal.controllers').controller("DefaultStep", function(scope, step, episode){
  if(step.model_api_name){
    if(!scope.editing[step.model_api_name] || !scope.editing[step.model_api_name].length){
      scope.editing.helper.addRecord(step.model_api_name);
    }
  }
});
