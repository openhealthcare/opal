var directives = angular.module('opal.directives', []);

directives.directive("freezePanes", function () {
    return function (scope, element, attrs) {
        scope.$watch("assignments", function () {
            $('table').stickyTableHeaders({fixedOffset: 123});
        });
    };
});

directives.directive('scrollTop', function () {
    return {
        link: function ($scope, element, attrs) {
            var body = $("body");
            element.bind("click", function(){
                body.animate({ scrollTop: "0" });
            });

            $(window).on("scroll.scrollTop", function(){
                window.requestAnimationFrame(function(){
                    if(body.scrollTop() > 0){
                        $(element).removeClass("hide");
                    }
                    else{
                        $(element).addClass("hide");
                    }
                });
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

directives.directive('setFocusIf', function($timeout) {
  return {
    link: function($scope, $element, $attr) {
      $scope.$watch($attr.setFocusIf, function(value) {
        if ( value ) {
          $timeout(function() {
            // We must reevaluate the value in case it was changed by a subsequent
            // watch handler in the digest.
            if ( $scope.$eval($attr.setFocusIf) ) {
              $element[0].focus();
            }
          }, 0, false);
        }
      });
    }
  }
});;

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
