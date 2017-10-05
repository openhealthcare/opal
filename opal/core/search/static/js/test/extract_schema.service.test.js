describe('ExtractSchema', function(){
    "use strict";

    var ExtractSchema, schema;

    var exampleSchemaData = [
        {
            "single":false,
            "name":"demographics",
            "display_name":"Demographics",
            "readOnly": true    ,
            "fields":[
                {
                    "title":"Name",
                    "lookup_list":null,
                    "name":"name",
                    "type":"string"
                }
            ]
        },
        {
            "name": "diagnosis",
            "single": false,
            "sort": 'date_of_diagnosis',
            "fields": [
                {"name": 'date_of_diagnosis', "type": 'date'},
                {"name": 'condition', "type": 'string'},
                {"name": 'provisional', "type": 'boolean'},
            ]
        },
        {
            "single": false,
            "name": "microbiology_test",
            "display_name": "Microbiology Test",
            "readOnly": false,
            "fields": [
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "MicrobiologyTest",
                name: "test",
                title: "Test",
                type: "string"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "MicrobiologyTest",
                name: "date_ordered",
                title: "Date Ordered",
                type: "date"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "MicrobiologyTest",
                name: "details",
                title: "Details",
                type: "string"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "MicrobiologyTest",
                name: "microscopy",
                title: "Microscopy",
                type: "string"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "MicrobiologyTest",
                name: "organism",
                title: "Organism",
                type: "string"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "MicrobiologyTest",
                name: "sensitive_antibiotics",
                title: "Sensitive Antibiotics",
                type: "string"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "MicrobiologyTest",
                name: "resistant_antibiotics",
                title: "Resistant Antibiotics",
                type: "string"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "MicrobiologyTest",
                name: "igm",
                title: "IGM",
                type: "string"
              },
            ],
        },
        {
            "single": false,
            "name": "investigation",
            "display_name": "Investigation",
            "readOnly": false,
            "fields": [
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "Investigation",
                name: "test",
                title: "Test",
                type: "string"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "Investigation",
                name: "date_ordered",
                title: "Date Ordered",
                type: "date"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "Investigation",
                name: "details",
                title: "Details",
                type: "string"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "Investigation",
                name: "microscopy",
                title: "Microscopy",
                type: "string"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "Investigation",
                name: "organism",
                title: "Organism",
                type: "string"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "Investigation",
                name: "sensitive_antibiotics",
                title: "Sensitive Antibiotics",
                type: "string"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "Investigation",
                name: "resistant_antibiotics",
                title: "Resistant Antibiotics",
                type: "string"
              },
              {
                default: null,
                description: null,
                enum: null,
                lookup_list: null,
                model: "Investigation",
                name: "igm",
                title: "IGM",
                type: "string"
              },
            ],
        }
    ];

    beforeEach(function(){
        module('opal.services');

        inject(function($injector) {
            ExtractSchema = $injector.get('ExtractSchema');
        })

        schema = new ExtractSchema(exampleSchemaData);
    });

    it('should keep a publically accessible version of columns', function(){
        var result = angular.copy(schema.columns);
        _.each(result, function(subrecord){
          _.each(subrecord.fields, function(field){
            delete field.subrecord;
          });
        });
        var expectedColumnNames = _.map(exampleSchemaData, function(c){ return c.name })
        var foundColumnNames = _.map(result, function(r){ return r.name });
        expect(foundColumnNames).toEqual(expectedColumnNames);
    });

    it('should restrict the fields to searchable fields for micro test', function(){
        var microTest = schema.findColumn('microbiology_test');
        var found = _.map(microTest.fields, function(mtf){
          return mtf.title;
        });
        var expected = [
          'Test',
          'Date Ordered',
          'Details',
          'Microscopy',
          'Organism',
          'Sensitive Antibiotics',
          'Resistant Antibiotics'
        ];

        expect(expected).toEqual(found);
    });

    it('should restrict the fields to searchable fields for investigations', function(){
        var microTest = schema.findColumn('microbiology_test');
        var found = _.map(microTest.fields, function(mtf){
          return mtf.title;
        });
        var expected = [
          'Test',
          'Date Ordered',
          'Details',
          'Microscopy',
          'Organism',
          'Sensitive Antibiotics',
          'Resistant Antibiotics'
        ];

        expect(expected).toEqual(found);
    });
});
