directives.directive("pathwayStep", function($controller, $parse){
  var controller =  function ($scope, $attrs) {
    var stepApiName = $attrs.pathwayStep;
    var pathway = $parse("pathway")($scope);
    var step = _.findWhere(pathway.steps, {api_name: stepApiName});
    $controller(step.step_controller, {
      scope: $scope,
      step: step,
      episode: pathway.episode
    });
    pathway.register(step.api_name, $scope);
  };
  return {
      restrict: 'EA', //Default in 1.3+
      controller: controller,
      scope: true,
  };
});

directives.directive("pathwayLink", function($parse){
  "use strict";
  return{
    link: function(scope, element, attrs){
      var pathwaySlug = attrs.pathwayLink;
      var episode = $parse(attrs.pathwayEpisode)(scope);
      var url = "/pathway/#/" + pathwaySlug;
      if(episode){
        url = url + "/" + episode.demographics[0].patient_id + "/" + episode.id;
      }
      element.attr("href", url);
    }
  };
});

directives.directive("openPathway", function($parse, $rootScope, Referencedata, Metadata, $modal, episodeLoader){
  /*
  * the open modal pathway directive will open a modal pathway for you
  * you can if you use the attribute pathway-callback="{{ some_function }}"
  * this function will get resolved with the result of pathway.save
  * it should return a function and will get resolved before the modal
  * closes
  */
  "use strict";

  return {
    scope: false,
    link: function(scope, element, attrs){
      $(element).click(function(e){
        e.preventDefault();
        var pathwayCallback;
        $rootScope.state = "modal";
        var pathwaySlug = attrs.openPathway;

        var episode = $parse(attrs.pathwayEpisode)(scope);

        if(attrs.pathwayCallback){
          // we bind the parse to be able to use scope with us overriding
          // episode id in the function
          pathwayCallback = _.partial($parse(attrs.pathwayCallback), _, scope);
        }
        else{
          pathwayCallback = function(){};
        }
        var template = "/pathway/templates/" + pathwaySlug + ".html?is_modal=True";
        return $modal.open({
          controller : 'ModalPathwayCtrl',
          templateUrl: template,
          size       : 'lg',
          resolve    :  {
            episode: function(){ return episode; },
            // todo we can't directly refer to episode like this
            pathwayDefinition: function(pathwayLoader){
              if(episode){
                return pathwayLoader.load(
                  pathwaySlug,
                  episode.demographics[0].patient_id,
                  episode.id
                );
              }
              else{
                return pathwayLoader.load(pathwaySlug);
              }
            },
            pathwayCallback: function(){ return pathwayCallback; },
            pathwayName: function(){ return pathwaySlug; },
            metadata: function(){ return Metadata.load(); },
            referencedata: function(){ return Referencedata.load(); },
          }
        });
      });
    }
  };
});

directives.directive("requiredIfNotEmpty", function(){
  /*
  * if we are saving multiple models we want to add validation
  * for a field to be required but only if one of the fields
  * is actually filled in
  */
  return {
    restrict: 'A',
    require: 'ngModel',
    scope: {"requiredIfNotEmpty": "="},
    link: function(scope, ele, attrs, ctrl){
      var validate = function(value){
        var valid;
        if(value){
          valid = true
        }
        else{
          valid = !_.find(scope.requiredIfNotEmpty, function(v, k){
            // can't use startswith because of phantomjs, but this does
            // the same trick
            return (k.indexOf("$$") !== 0) && v
          });
        }

        ctrl.$setValidity('requiredIfNotEmpty', valid);
        return valid;
      }

      scope.$watch("requiredIfNotEmpty", function(){
        validate(ctrl.$viewValue);
      }, true);

      ctrl.$validators.requiredIfNotEmpty = function(value){
        var valid = validate(value);
        ctrl.$setValidity('requiredIfNotEmpty', valid);
        return valid;
      };
    }
  }
});
