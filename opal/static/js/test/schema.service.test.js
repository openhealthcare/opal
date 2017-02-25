describe('schema', function(){
    "use strict";

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
        },
        {
            name: "diagnosis",
            single: false,
            sort: 'date_of_diagnosis',
            fields: [
                {name: 'date_of_diagnosis', type: 'date'},
                {name: 'condition', type: 'string'},
                {name: 'provisional', type: 'boolean'},
            ]
        }
    ];

    beforeEach(function(){
        module('opal.services');

        inject(function($injector) {
            Schema = $injector.get('Schema');
        })

        schema = new Schema(exampleSchemaData);
    })

    it('should keep a publically accessible version of the columns', function(){
        expect(schema.columns).toEqual(exampleSchemaData);
    })

    it('should throw an error if asked for a non-column', function() {
        expect(function(){ schema.getColumn('notarealcolumn'); })
            .toThrow(new Error('No such column with name: "notarealcolumn"'))
    });

    it('should recognise singletons', function(){
        expect(schema.isSingleton("demographics")).toBeFalsy();
        expect(schema.isSingleton("tagging")).toBeTruthy();
        expect(schema.isSingleton("diagnosis")).not.toBeTruthy();
    });

    it('should recognise read only', function(){
        expect(schema.isReadOnly("tagging")).toBeFalsy();
        expect(schema.isReadOnly("demographics")).toBeTruthy();
    });

    it('should filter advanced searchable columns', function () {
        expect(schema.getAdvancedSearchColumns()).toEqual([exampleSchemaData[1]]);
    });

    it('should be able to get the number of columns', function() {
        expect(schema.getNumberOfColumns()).toBe(3);
    });
});
