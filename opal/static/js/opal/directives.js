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
    return {
      restrict: 'A',
      link: function (scope, element, attrs) {
          var $el = $(element).find('table');

          $el.stickyTableHeaders({
              scrollableArea: $(element),
          });
      }
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

directives.directive('goToTop', function () {
    return {
        priority: 1,
        link: function (scope, element, attrs) {
            element.bind("click", function(){
                var body = $("html, body");
                body.scrollTop(0);
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

directives.directive('autofocus', ['$timeout', function($timeout) {
  return {
    restrict: 'A',
    link : function($scope, $element) {
      $scope.$watch('autofocus', function(){
        $timeout(function() {
          $element[0].focus();
        });
      });
    }
  };
}]);

// a nice little directive to disable
// a button on click unless we tell it otherwise
directives.directive('oneClickOnly', function(){
  return {
    link: function($scope, $element, attrs){
      if(attrs.oneClickOnly === undefined || !attrs.oneClickOnly){
        $element.on('click', function(){
          if(!$element.prop('disabled')){
            $element.prop( "disabled", true );
          }
        });
      }
    }
  };
});

directives.directive('clipboard', function(growl) {
    "use strict";
    // The MIT License (MIT)
    // Copyright (c) 2015 Sachin N
    // copied from https://github.com/sachinchoolur/ngclipboard
    // extended to give a growl notification by default

    var GROWL_SUCCESS = "Copied";
    var GROWL_FAILURE = "Failed to copy";

    return {
        restrict: 'A',
        scope: {
            clipboardSuccess: '&',
            clipboardError: '&',
            clipboardShowGrowl: '=',
        },
        link: function(scope, element) {
            var clipboard = new Clipboard(element[0]);

            clipboard.on('success', function(e) {
              scope.$apply(function () {
                if(scope.clipboardShowGrowl !== false){
                  growl.success(GROWL_SUCCESS);
                }
                scope.clipboardSuccess({
                  e: e
                });
              });
            });

            clipboard.on('error', function(e) {
              scope.$apply(function () {
                if(scope.clipboardShowGrowl !== false){
                    growl.error(GROWL_FAILURE + ' ' + e);
                }
                scope.clipboardError({
                  e: e
                });
              });
            });
        }
    };
});


directives.directive("dateOfBirth", function(){
  return {
    require: "?ngModel",
    scope: true,
    template: "<input name='[[ name ]]' class='form-control' ng-pattern='numberCheck' ng-model='value' ng-model-options=\"{ updateOn: 'blur' }\" ng-change='onChange()'>",
    link: function(scope, element, attrs, ngModel){
      if (!ngModel) return;

      scope.name = attrs.name

      scope.onChange = function(){
        ngModel.$setViewValue(moment(scope.value, "DD/MM/YYYY", true));
      };

      scope.numberCheck = {test: function(inputStr){

        if(_.last(inputStr.split("/")).length > 4){
            return false;
        }

        var inputMoment =  moment(inputStr, "DD/MM/YYYY", true);
        if(!inputMoment.isValid()){
            return false;
        }

       	var now = moment();

        // I wasn't born yesterday, don't let people be born tomorrow
        if(inputMoment.isAfter(now)){
            return false;
        }

        // lets not allow for patients over 150
        return now.diff(inputMoment, 'years') < 150
      }}

      ngModel.$render = function(){
        if(_.isString(ngModel.$modelValue)){
            scope.value = ngModel.$modelValue;
        }
        else{
            if(ngModel.$modelValue){
                scope.value = moment(ngModel.$modelValue).format("DD/MM/YYYY");
            }
            else{
                scope.value = undefined;
            }
        }
      };
    }
  };
});


directives.directive("tagSelect", function(Metadata){
  return {
    require: "?ngModel",
    scope: true,
    templateUrl: "/templates/ng_templates/tag_select.html",
    link: function(scope, element, attrs, ngModel){
      if (!ngModel) return;
      Metadata.then(function(metadata){
        scope.onRemove = function($item, $model){
            ngModel.$modelValue[$model] = false;
        };

        scope.onSelect = function($item, $model){
            ngModel.$modelValue[$model] = true;
        };

        ngModel.$render = function(){
          // get all existing tag names that are direct add
          // filter the meta data tags for these
          // return the meta data
          var tagNames = [];
          scope.something = [];

          _.each(ngModel.$modelValue, function(v, k){
              if(v){
                tagNames.push(k);
              }
          })

          scope.value = _.filter(metadata.tags, function(tagData){
            return _.contains(tagNames, tagData.name) && tagData.direct_add;
          });

          scope.tagsList = _.filter(_.values(metadata.tags), function(option){
              return option.direct_add;
          }).sort(function(x, y){ return y.name < x.name; });
        };
      });
    }
  };
});
