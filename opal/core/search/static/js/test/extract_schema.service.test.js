describe('schema', function(){
    "use strict";

    var ExtractSchema, schema;

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
            ExtractSchema = $injector.get('ExtractSchema');
        })

        schema = new ExtractSchema(exampleSchemaData);
    })

    it('should keep a publically accessible version of the columns', function(){
        var result = angular.copy(schema.columns);
        _.each(result, function(subrecord){
          _.each(subrecord.fields, function(field){
            delete field.subrecord;
          });
        });
        expect(result).toEqual(exampleSchemaData);
    })

    it('should return the find the field', function(){
      expect(!!schema.findField("demographics", "name")).toEqual(true);
    });

    it('should set up a reference on fields to the subrecord', function(){
        expect(schema.columns[0].fields[0].subrecord).toBe(schema.columns[0]);
    });

    it('should throw an error if the subrecord field has already been populated', function(){
      var flawedSchemaData = angular.copy(exampleSchemaData);
      flawedSchemaData[0].fields[0].subrecord = "bah";
      expect(function(){ new ExtractSchema(flawedSchemaData);}).toThrow();
    });

    it('should filter advanced searchable columns', function () {
        var expected = [angular.copy(exampleSchemaData[1])];
        _.each(expected, function(e){
          _.each(e.fields, function(f){
            f.subrecord = e;
          });
        });
        expect(schema.getAdvancedSearchColumns()).toEqual(expected);
    });
});
