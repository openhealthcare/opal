angular.module('opal.controllers').controller('PathwayCtrl', function(
    $scope,
    pathwayDefinition,
    episode,
    referencedata,
    metadata,
    $injector,
    $window
){
    "use strict";
    $scope.metadata = metadata;
    _.extend($scope, referencedata.toLookuplists());
    $scope.episode = episode;
    var pathwayService = $injector.get(
        pathwayDefinition.pathway_service
    );
    $scope.pathway = new pathwayService(pathwayDefinition, episode);
    $scope.editing = $scope.pathway.populateEditingDict(episode);
    $scope.pathway.pathwayPromise.then(function(response){
      $window.location.href = response.redirect_url;
    }, function(error){
      $window.alert("unable to save patient");
    });
});
