describe('services.TagService', function() {
    "use strict";
    var tagService;
    var exampleOptions = {
      "tags": {
        id_inpatients: {
              "visible_in_list": true,
              "direct_add": true,
              "display_name": "ID Inpatients",
              "slug": "infectious_diseases-id_inpatients",
              "name": "id_inpatients"
        },
        tropical: {
              "visible_in_list": true,
              "direct_add": true,
              "display_name": "Tropical",
              "slug": "infectious_diseases-tropical",
              "name": "tropical"
        },
        infectious_diseases: {
            "visible_in_list": true,
            "direct_add": false,
            "display_name": "Infectious Diseases",
            "slug": "infectious_diseases",
            "name": "infectious_diseases"
        }
      }
    };


    var exampleOptionsPromise = {
        then: function(x){
            x(angular.copy(exampleOptions));
        }
    };

    beforeEach(function(){
        module('opal.services', function($provide){
            $provide.constant('Options', exampleOptionsPromise);
        });
        var TagService;

        inject(function($injector){
            TagService = $injector.get('TagService');
        });

        tagService = new TagService(["id_inpatients", "infectious_diseases"]);
    });

    describe('TagService', function(){
        it("should put the visible options onto itself when they arrive and sort them alphabetically", function(){
            expect(tagService.tags_list ).toEqual([
              exampleOptions.tags.id_inpatients,
              exampleOptions.tags.tropical
            ]);
        });

        it("should only put visible tags onto itself", function(){
            expect(tagService.currentFormTags).toEqual(
                [exampleOptions.tags.id_inpatients.name]
            );
        });

        it("to save should cast its own tags to an object", function(){
            expect(tagService.toSave()).toEqual(
                {id_inpatients: true, infectious_diseases: true}
            );
        });
    });
});
