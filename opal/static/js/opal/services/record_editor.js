angular.module('opal.services').factory('RecordEditor', function(
    $q, $modal, $rootScope, $routeParams, UserProfile
){
  "use strict";
  var RecordEditor = function(episode){
    var self = this;

    self.getItem = function(name, iix){
      if (episode[name] && episode[name][iix] && episode[name][iix].columnName) {
          return episode[name][iix];
      } else {
          return episode.newItem(name, {column: $rootScope.fields[name]});
      }
    };

    self.openEditItemModal = function(item, name, template_url){
      $rootScope.state = 'modal';
      if(!template_url){
        template_url = '/templates/modals/' + name + '.html/';
      }

      if($routeParams.slug){
          template_url += $routeParams.slug;
      }

      var deferred = $q.defer();

      UserProfile.load().then(function(profile){
        if(profile.readonly){
            deferred.resolve();
        }
        else{
          var modal_opts = {
              backdrop: 'static',
              templateUrl: template_url,
              controller: item.formController,
              resolve: {
                  item: function() { return item; },
                  profile: profile,
                  episode: function() { return episode; },
                  metadata: function(Metadata) { return Metadata.load(); },
                  referencedata: function(Referencedata){ return Referencedata.load(); }
              }
          };

          var modal = $modal.open(modal_opts);

          modal.result.then(function(result) {
            $q.when(result).then(function(x){
              $rootScope.state = 'normal';
              deferred.resolve(result);
            });
          });
        }
      });

      return deferred.promise;
    };

    self.editItem = function(name, item, url){
      return self.openEditItemModal(item, name, url);
    };

    self.newItem = function(name, url){
      var iix = episode[name].length;
      var item = self.getItem(name, iix);

      if(item.isReadOnly() || item.isSingleton()){
        var deferred = $q.defer();
        deferred.resolve();
        return deferred.promise;
      }
      return self.openEditItemModal(item, name, url);
    };
  };

  return RecordEditor;
});
