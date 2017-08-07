angular.module('opal.services').service('WizardPathway', function(Pathway){
  "use strict";
  var WizardPathway = function(pathwayDefinition, episode){
    Pathway.call(this, pathwayDefinition, episode);
    this.currentIndex = 0;
    this.numSteps = this.steps.length;
    this.currentStep = this.steps[this.currentIndex];
    this.history = [];
  };

  WizardPathway.prototype = angular.copy(Pathway.prototype);
  var additionalPrototype = {
    hasNext: function(){
      return this.currentIndex + 1 != this.steps.length;
    },
    hasPrevious: function(){
      return this.history.length;
    },
    goNext: function(editing){
      this.history.push(this.currentStep.api_name);
      this.goToStep(this.steps[this.currentIndex + 1].api_name);
    },
    stepIndex: function(stepApiName){
      var idx = _.findIndex(this.steps, function(someStep){
          return someStep.api_name  === stepApiName;
      });

      if(idx === -1){
        throw 'unable to find ' + stepApiName
      }

      return idx;
    },
    goPrevious: function(editing){
      this.goToStep(this.history.pop())
    },
    showNext: function(editing){
      return true;
    },
    goToStep: function(stepApiName){
      var stepIndex = this.stepIndex(stepApiName);
      this.currentIndex = stepIndex;
      this.currentStep = this.steps[stepIndex];
    }
  };
  _.extend(WizardPathway.prototype, additionalPrototype);
  return WizardPathway;
});
