var directives = angular.module('opal.directives', []);

directives.directive("freezePanes", function () {
    return function (scope, element, attrs) {
        scope.$watch("assignments", function () {
            $('table').stickyTableHeaders({fixedOffset: 114});
                //$('table').stickyTableHeaders()
        });
    };
});


directives.directive('loadingbar', function($rootScope) {
	return {
		link: function(scope, element, attrs) {
			element.addClass('hide');

			$rootScope.$on('$routeChangeStart', function() {
				element.removeClass('hide');
			});

			$rootScope.$on('$routeChangeSuccess', function() {
				element.addClass('hide');
			});
		}
	};
});

directives.directive('placeholder', function($timeout){
	if ($.support.placeholder) {
		return {};
	}
	return {
		link: function(scope, elm, attrs){
			if (attrs.type === 'password') {
				return;
			}
			$timeout(function(){
				elm.val(attrs.placeholder).focus(function(){
					if ($(this).val() == $(this).attr('placeholder')) {
						$(this).val('');
					}
				}).blur(function(){
					if ($(this).val() == '') {
						$(this).val($(this).attr('placeholder'));
					}
				});
			});
		}
	}
});

directives.directive('markdown', function () {
	return function postLink (scope, element, attrs) {
	    
	    var prefix = 'item';
	    if( _.isUndefined(scope['item']) ){
		if(! _.isUndefined(scope['editing']) )
		    {
			prefix = 'editing';
		    }
		else
		    {
			return;
		    }
	    }
	    scope.$watch(prefix + '.' + attrs.markdown, function(){
		    var converter = new Showdown.converter({extensions: [OpalDown]});
            if(scope[prefix][attrs.markdown]){
                var contents = converter.makeHtml(scope[prefix][attrs.markdown]);
		        element.html(contents);
            }
		}
		);
	}
});

directives.directive('focusOnThis', function($timeout){
    return {
        link: function(scope, elem, attr){
            $timeout(function(){
                elem[0].focus();
            });
        }
    }
});

angular.module('ui.bootstrap.modal').directive('modalWindow', function ($timeout) {
  return {
    priority: 1,
    link: function (scope, element, attrs) {
      $timeout(function () {
        element.find('[autofocus]').focus();
      });
    }
  };
});
