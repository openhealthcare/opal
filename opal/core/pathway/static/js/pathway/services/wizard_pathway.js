angular.module('opal.services').service('WizardPathway', function(Pathway){
  "use strict";
  var WizardPathway = function(pathwayDefinition, episode){
    Pathway.call(this, pathwayDefinition, episode);
    this.currentIndex = 0;
    this.numSteps = this.steps.length;
    this.currentStep = this.steps[this.currentIndex];
  };

  WizardPathway.prototype = angular.copy(Pathway.prototype);
  var additionalPrototype = {
    hasNext: function(){
        return this.currentIndex + 1 != this.steps.length;
    },
    hasPrevious: function(){
        return this.currentIndex > 0;
    },
    next: function(currentIndex, currentStep){
        return this.currentIndex + 1;
    },
    previous: function(currentIndex, currentStep){
        return this.currentIndex - 1;
    },
    goNext: function(editing){
      this.currentIndex = this.next(this.currentIndex, this.currentStep);
      this.currentStep = this.steps[this.currentIndex];
    },
    stepIndex: function(step){
      return _.findIndex(this.steps, function(someStep){
          return someStep.display_name  === step.display_name;
      });
    },
    goPrevious: function(editing){
      this.currentIndex = this.previous(this.currentIndex, this.currentStep);
      this.currentStep = this.steps[this.currentIndex];
    },
    showNext: function(editing){
        return true;
    }
  };
  _.extend(WizardPathway.prototype, additionalPrototype);
  return WizardPathway;
});
