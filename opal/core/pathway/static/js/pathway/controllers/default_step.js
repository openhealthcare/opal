angular.module('opal.controllers').controller("DefaultStep", function(scope, step, episode){
  "use strict";
  // we don't want an empty form.
  // if there is no model already, add one in

  if(step.model_api_name){
    if(!scope.editing[step.model_api_name] || !scope.editing[step.model_api_name].length){
      scope.editing.helper.addRecord(step.model_api_name);
    }
  }
});
