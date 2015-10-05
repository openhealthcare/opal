var directives = angular.module('opal.directives', []);

directives.directive("fixHeight", function () {
    return function (scope, element, attrs) {
        function calcParams(){
            var stickyNavHeight = $("#main-navbar").height();
            var footerHeight = $("footer").height();
            return $(element).offset().top + stickyNavHeight + footerHeight;
        }

        function updateHeight(){
            $(element).height($(window).height() - calcParams());
        }

        updateHeight();

        $(window).on("resize.fixHeight", updateHeight);

        scope.$on('$destroy', function(){
          $(window).off("resize.fixHeight");
        });
    };
});

directives.directive("scrollEpisodes", function(){
    return function(scope, element, attrs){
      /*
      * when they user is on an episode and presses the down up key, the selected
      * episode should always be shown in its entirety.
      */
      var shouldScroll = attrs.scrollEpisodes,
          patientListContainer = $(attrs.scrollContainer),
          thHeight = patientListContainer.find("thead").height();

      var adjustForThead = function(){
        if($(element).position().top <= thHeight){
          // adjust for the thead, plus some buffer
          patientListContainer.scrollTop(patientListContainer.scrollTop() - thHeight - 10);
        }
      }

      function isScrolledIntoView(element, parent){
        var elementTop    = element.getBoundingClientRect().top ,
            elementBottom = element.getBoundingClientRect().bottom;
        return elementTop >= thHeight && elementBottom <= window.innerHeight;
      }

      scope.$on('keydown', function(event, e) {
        if(scope[shouldScroll](scope.row)){
            // up
            if(e.keyCode === 38){
              event.preventDefault();
              if(!isScrolledIntoView(element[0], patientListContainer[0])){
                element[0].scrollIntoView(true);
              }
              adjustForThead();
            }
            // down
            else if(e.keyCode === 40){
              event.preventDefault();
              if(!isScrolledIntoView(element[0], patientListContainer[0])){
                element[0].scrollIntoView(false);
              }
              adjustForThead();
            }
        }
      });
    };
});

directives.directive("freezeHeaders", function () {
    return function (scope, element, attrs) {
        var $el = $(element).find('table');
        $el.stickyTableHeaders({
            scrollableArea: $(element),
        });
    };
});

directives.directive('scrollTop', function () {
    return {
        link: function (scope, element, attrs) {
            var body = $("html, body");
            element.bind("click", function(){
                body.animate({ scrollTop: "0" });
            });

            $(window).on("scroll.scrollTop", function(){
                window.requestAnimationFrame(function(){
                    if($(window).scrollTop() > 0){
                        $(element).removeClass("hidden-at-top");
                    }
                    else{
                        $(element).addClass("hidden-at-top");
                    }
                });
            });

            scope.$on('$destroy', function(){
              $(window).off("resize.fixHeight");
            });
        }
    };
});

directives.directive('blurOthers', function(){
    return {
        link: function ($scope, element, attrs) {
            $scope.$watch(attrs.blurOthers, function(value){
                if(attrs.blurOthers){
                    $(document.activeElement).blur();
                }
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

directives.directive('slashKeyFocus', function() {
  return {
    link: function(scope, elem, attrs) {
        scope.$watch(attrs.slashKeyFocus, function(value){
            if(value){
                $(window).on("keyup.keyFocus", function(e){
                    // if we're already focused on a text area, lets ignore this
                    if (e.keyCode == 191 && !e.shiftKey) {
                        if(!$('input:focus, textarea:focus').length){
                            $(elem).focus();
                        }
                    }
                });
            } else {
                $(window).off("keyup.keyFocus");
            }

            $elem = $(elem);

            $elem.on("focus.keyFocus", function(x){
                $elem.on("keyup.keyBlur", function(e){
                    if (e.keyCode == 27) {
                        $elem.blur();
                    }
                });
            });

            $elem.on("blur.keyFocus", function(x){
                $(elem.off("keyup.keyBlur"));
            });
        });
    }
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

// until bootstrap moves to flex box, lets grab the parent height with javascript
directives.directive('parentHeight', function(){
  return{
    restrict: 'A',
    link: function(scope, element){
      var $element = $(element);
      $element.css("min-height", $element.parent().height());
    }
  };
});

directives.directive('autofocus', function($timeout) {
  return {
    restrict: 'A',
    link : function($scope, $element) {
      $timeout(function() {
        $element[0].focus();
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
