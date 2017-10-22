describe('Schema', function(){
  "use strict";

  var Schema, schema;

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
              },
              {
                  "title": "Deceased",
                  "lookup_list": null,
                  "name": "dead",
                  "type": "boolean"
              },
              {
                  "title": "Date of Birth",
                  "lookup_list": null,
                  "name": "date_of_birth",
                  "type": "date"
              },
              {
                  "title": "Age",
                  "lookup_list": null,
                  "name": "age",
                  "type": "integer"
              },
              {
                  "title": "Last Appointment",
                  "lookup_list": null,
                  "name": "last_appointment",
                  "type": "date_time"
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
      },
      {
          "single": false,
          "name": "symptoms",
          "display_name": "Symptoms",
          "readOnly": false,
          "fields": [
              {
                  "title": "Symptoms",
                  "lookup_list": "symptoms",
                  "name": "symptoms",
                  "type": "many_to_many"
              },
              {
                  "title":"Consistency Token",
                  "lookup_list":null,
                  "name":"consistency_token",
                  "type":"token"
              },
              {
                  "title":"Created",
                  "lookup_list":null,
                  "name":"created",
                  "type":"date_time"
              }
          ]
      }
  ];

  beforeEach(function(){
    module('opal.services');

    inject(function($injector) {
        Schema = $injector.get('Schema');
    })

    schema = new Schema(exampleSchemaData);
  });

  describe('Chunk columns', function(){
    it('should chunk columns into columns of 6', function(){
      var example = [1, 2, 3, 4, 5, 6, 7, 8];
      var chunked = schema.chunkColumns(example);
      var expected = [[1, 2, 3, 4, 5, 6], [7, 8]];
      expect(chunked).toEqual(expected);
    });

    it('should have chunked columns', function(){
      expect(_.isArray(schema.chunkedColumns)).toBe(true);
    });
  });

  describe('Checking field type', function(){
    it('should be falsy for non fields', function(){
        expect(schema.isType()).toBe(false);
    });

    it('should be falsy for nonexistent fields', function(){
        expect(schema.isType("demographics", "towel_preference")).toBe(false);
    });

    it('should find boolean fields', function(){
        expect(schema.isBoolean("demographics", "dead")).toEqual(true);
    });

    it('should find select many fields', function(){
        spyOn(schema, "isType").and.returnValue(true);
        expect(schema.isSelectMany("demographics", "dead")).toEqual(true);
        expect(schema.isType).toHaveBeenCalledWith(
          "demographics", "dead", "many_to_many_multi_select"
        );
    });

    it('should find string fields', function(){
        expect(schema.isText("demographics", "name")).toBe(true);
    });

    it('should find select fields', function(){
        expect(schema.isSelect("symptoms", "symptoms")).toBe(true);
    });

    it('should find date fields', function(){
        expect(schema.isDate("demographics", "date_of_birth")).toBe(true);
    });

    it('should find number fields', function(){
        expect(schema.isNumber("demographics", "age")).toBe(true);
    });

    it('should find date time fields', function(){
        expect(schema.isDateTime("demographics", "last_appointment")).toBe(true);
    });

    it('should find date type fields', function(){
        expect(schema.isDateType("demographics", "date_of_birth")).toBe(true);
    });
  });

  it('should keep a publically accessible version columns', function(){
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

  describe('getChoices', function(){
    it('should get a lookup list and suffix it', function(){
      spyOn(schema, "findField").and.returnValue({
        lookup_list: "dogs"
      });
      var referencedata = jasmine.createSpyObj(["get"])
      referencedata.get.and.returnValue(['Poodle', 'Dalmation']);
      var result = schema.getChoices("some", "field", referencedata);
      expect(result).toEqual(['Poodle', 'Dalmation']);
      expect(referencedata.get).toHaveBeenCalledWith("dogs");
    });

    it('should get an enum', function(){
      spyOn(schema, "findField").and.returnValue({
        enum: [1, 2, 3]
      });
      var result = schema.getChoices("some", "field");
      expect(result).toEqual([1, 2, 3]);
    });
  });
});
