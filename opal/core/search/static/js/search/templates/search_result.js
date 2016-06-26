(function(window, document, undefined) {
  'use strict';

  angular.module('opal.services').run([ '$templateCache', function($templateCache) {
    var template_string = '<h4 class="inline orange">';
    template_string += '[[ match.value.first_name ]] [[ match.value.surname ]] ';
    template_string += '</h4>';
    template_string += '<span ng-show="match.value.dateOfBirth">';
    template_string += '([[ match.value.dateOfBirth | shortDate ]])';
    template_string += '</span>';
    template_string += '<div>';
    template_string += '[[ match.value.hospitalNumber ]]'
    template_string += ' - Episode<span ng-show="match.value.count > 1">s</span> ([[ match.value.categories|title ]]) [[ match.value.years ]]'
    template_string += '</div>';

    $templateCache.put('search/search_result.html', template_string);
    $templateCache.put('search/search_results.html', '<ul tabindex="-1" class="typeahead dropdown-menu" ng-show="$isVisible()" role="select"><li role="presentation" ng-repeat="match in $matches" ng-class="{active: $index == $activeIndex}"><a role="menuitem" class="search-dropdown-result" tabindex="-1" ng-click="$select($index, $event)" ng-include="\'search/search_result.html\'"></a></li></ul>');
  } ]);
})(window, document);
