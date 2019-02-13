directives.directive("saveMultipleWrapper", function($parse){
  /*
    a utility directive that allows us to code
    as if we had an array of editings and save
    them in a pathway appropriately
    it adds into the child scope

    models.subrecords an array of the appropriate models
    remove a function that takes in an index and will remove that from the array
    addAnother a function that will add another to an array

    by default it will add an empty model if there isn't one already

    example usage

    <div save-multiple-wrapper="editing.treatment">
      <div ng-repeat="editing in model.subrecords">
        {% input field="Treatment.drug" %}
        <button ng-click="remove($index)"></button>
      </div>

      <button ng-click="addAnother()"></button>
    </div>
  */
  return {
    transclude: true,
    template: '<div ng-transclude></div>',
    scope: {
      parentModel: "=saveMultipleWrapper",
    },
    link: function(scope, element, attrs, ctrl, transclude){
      var sc = scope.$parent.$new();
      var editingString = attrs.saveMultipleWrapper;

      if(!sc.model_name){
        sc.model_name = editingString.substr(editingString.indexOf(".")+1);
      }

      var getNewRecord = function(){
        return {
          _client: {
            completed: false,
            id: _.uniqueId(sc.model_name)
          }
        }
      }

      var getModel = $parse(sc.model_name);

      // in pathways we save multiple models of the same type as arrays
      if(!scope.parentModel){
        scope.parentModel = [getNewRecord()];
      }
      else{
        if(!_.isArray(scope.parentModel)){
          // this shouldn't be necessary, the only time
          // this happens if its a singleton, when we shouldn't
          // be add to many, but let's be flexible...
          scope.parentModel = [scope.parentModel];
        }
        _.each(scope.parentModel, function(pm){
          if(!pm._client){
            pm._client = {};
          }
          if(!_.has(pm._client, "completed")){
            pm._client.completed = true;
          }
        });
      }

      if(!scope.parentModel.length){
        scope.parentModel.push(getNewRecord());
      }

      sc.model = {subrecords: []};

      // make sure these don't override the controller
      if(!sc.remove){
        sc.remove = function($index){
          sc.model.subrecords.splice($index, 1);
        };
      }

      if(!sc.done){
        sc.done = function(subrecord){
          if(!subrecord._client){
            subrecord._client = {};
          }
          subrecord._client.completed = true;
        }
      }

      if(!sc.recordFilledIn){
        /*
        * we try and find out if the user
        * has populated the subrecord
        */
        sc.recordFilledIn = function(subrecord){
          var subrecordKeys = _.keys(subrecord);
          return _.filter(subrecordKeys, function(k){
            if(k == "_client" || k.indexOf("$") == 0){
              return false;
            }
            if(_.isString(subrecord[k]) && !subrecord[k].length){
               return false;
            }
            return true;
          }).length;
        }
      }

      if(!sc.edit){
        sc.edit = function(subrecord){
          if(!subrecord._client){
            subrecord._client = {};
          }
          subrecord._client.completed = false;
        }
      }

      if(!sc.addAnother){
        sc.addAnother = function(){
            var newModel = {};
            newModel[sc.model_name] = getNewRecord();
            sc.model.subrecords.push(newModel);
        };
      }
      var updateParent = true;
      var updateChild = true;

      sc.$watchCollection(attrs.saveMultipleWrapper, function(){
        if(updateParent){
          updateChild = false;
          sc.model.subrecords.splice(0, sc.model.subrecords.length);
          _.each(scope.parentModel, function(pm){
              var editing = {};
              editing[sc.model_name] = pm;
              sc.model.subrecords.push(editing);
          });
          updateChild = true;
        }
      });

      // deep watch any changes and when they're done
      // copy them onto the parent model
      sc.$watchCollection("model.subrecords", function(){
        if(updateChild){
          updateParent = false;
          var children = _.map(sc.model.subrecords, function(someEditing){
              return getModel(someEditing);
          });

          scope.parentModel.splice(0, scope.parentModel.length);
          _.each(children, function(child){
            scope.parentModel.push(child);
          });
          updateParent = true;
        }
      });

      transclude(sc, function(clone, scope) {
          element.empty();
          element.append(clone);
      });
    }
  };
});

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

directives.directive("openPathway", function($parse, $rootScope, $modal, $q,
                                             Referencedata, Metadata,
                                             episodeLoader){
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

        var deferred = $q.defer();

        $modal.open({
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
        }).result.then(
          function(what){
            $rootScope.state = 'normal';
            deferred.resolve(what);
          },
          function(what_now){
            $rootScope.state = 'normal';
            deferred.resolve(what_now);
          }
        )

        return deferred.promise;
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
