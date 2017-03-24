///
/// Provide nice friendly 'alerts' for Opal
///
angular.module('opal.services')
    .factory('Alert', function($modal, $rootScope, $q){
        var Alert = {
            open: function(message, title, dismiss_text, template){
                var deferred = $q.defer()
                var templateUrl = template || '/templates/modals/alert.html';
                dismiss_text = dismiss_text || 'OK';
                var modal = $modal.open({
                    templateUrl: templateUrl,
                    controller : 'AlertCtrl',
                    resolve    : {
                        title       : function(){ return title },
                        message     : function(){ return message },
                        dismiss_text: function(){ return dismiss_text }
                    }
                });
                $rootScope.state = 'modal';
                modal.result.then(
                    function(){
                        $rootScope.state = 'normal';
                        deferred.resolve();
                    },
                    function(){
                        $rootScope.state = 'normal';
                        deferred.reject();
                    });
                return deferred.promise
            }
        };
        return Alert
    })
