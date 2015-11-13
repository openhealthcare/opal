describe('schema', function(){
    var Schema, schema;

    var exampleSchemaData = [
        {
            "single": true,
            "advanced_searchable": false,
            "readOnly": false,
            "name": "tagging",
            "display_name":"Teams",
            "fields":[
                {"name":"opat","type":"boolean"},
                {"name":"opat_referrals","type":"boolean"},
            ]
        },
        {
            "single":false,
            "name":"demographics",
            "display_name":"Demographics",
            "readOnly": true    ,
            "advanced_searchable": true,
            "fields":[
                {
                    "title":"Consistency Token",
                    "lookup_list":null,
                    "name":"consistency_token",
                    "type":"token"
                },
                {
                    "title":"Name",
                    "lookup_list":null,
                    "name":"name",
                    "type":"string"
                }
            ]
        }
    ]

    beforeEach(function(){
        module('opal', function($provide) {
            $provide.value('$analytics', function(){
                return {
                    pageTrack: function(x){}
                }
            });

            $provide.provider('$analytics', function(){
                this.$get = function() {
                    return {
                        virtualPageviews: function(x){},
                        settings: {
                            pageTracking: false,
                        },
                        pageTrack: function(x){}
                     };
                };
            });
        });
    });

    beforeEach(function(){
        module('opal.services');

        inject(function($injector) {
            Schema = $injector.get('Schema');
        })

        schema = new Schema(exampleSchemaData);
    })

    it('should filter advanced searchable columns', function () {
        expect(schema.getAdvancedSearchColumns()).toEqual([exampleSchemaData[1]]);
    });

    it('should keep a publically accessible version of the columns', function(){
        expect(schema.columns).toEqual(exampleSchemaData);
    })

    it('should recognise singletons', function(){
        expect(schema.isSingleton("demographics")).toBeFalsy();
        expect(schema.isSingleton("tagging")).toBeTruthy();
    });

    it('should recognise read only', function(){
        expect(schema.isReadOnly("tagging")).toBeFalsy();
        expect(schema.isReadOnly("demographics")).toBeTruthy();
    });
});
