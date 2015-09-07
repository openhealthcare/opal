var directives = angular.module('opal.directives', []);

directives.directive("freezeHeaders", function ($timeout) {
    return function (scope, element, attrs) {
        $timeout(function() {
            var onWindow = false;
            var $el = $(element).find('table');
            var stickyNavHeight, breakPoint;

            function calcParams(){
                stickyNavHeight = $("#main-navbar").height();
                breakPoint = $(element).offset().top - stickyNavHeight;
            }

            function reCalculateMenu(){
                if($(window).scrollTop() < breakPoint && onWindow){
                    onWindow = false;
                    $el.stickyTableHeaders({
                        scrollableArea: $(element),
                        fixedOffset: 0
                    });
                }

                if($(window).scrollTop() > breakPoint && !onWindow){
                    onWindow = true;
                    $el.stickyTableHeaders({
                        scrollableArea: window,
                        fixedOffset: stickyNavHeight
                    });
                }
            }

            calcParams();

            $el.stickyTableHeaders({
                scrollableArea: $(element)
            });

            $(window).on("resize.changeScrollViewPort", function(){
                calcParams();
            });

            $(window).on("scroll.changeScrollViewPort", function(){
                requestAnimationFrame(reCalculateMenu);
            });
        });
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
					if ($(this).val() === '') {
						$(this).val($(this).attr('placeholder'));
					}
				});
			});
		}
	};
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
	};
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
  };
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
