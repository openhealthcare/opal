describe('services', function() {
    "use strict";

    var $rootScope, FieldTranslater, patientData, jsPatientData;

    beforeEach(module('opal.services'));

    beforeEach(inject(function($injector){
        $rootScope   = $injector.get('$rootScope');
        FieldTranslater = $injector.get('FieldTranslater');
    }));

    beforeEach(function() {
        var columns = {
            "fields": {
                'demographics': {
                    name: "demographics",
                    single: true,
                    fields: [
                        {name: 'name', type: 'string'},
                        {name: 'date_of_birth', type: 'date'},
                        {name: 'created', type: 'date_time'},
                        {name: 'age', type: 'integer'},
                        {name: 'weight', type: 'float'},
                    ]
                },
            }
        };
        $rootScope.fields = columns.fields;

        patientData = {
            id: 123,
            date_of_admission: "19/11/2013",
            active: true,
            discharge_date: null,
            date_of_episode: null,
            demographics: [{
                id: 101,
                name: 'John Smith',
                date_of_birth: '31/07/1980',
                hospital_number: '555',
                created: "07/04/2015 11:45:00",
                age: "36",
                weight: "20.2",
                sex: null
            }],
        };


        jsPatientData = {
            id: 123,
            date_of_admission: moment(new Date(2013, 10, 19)),
            active: true,
            discharge_date: null,
            date_of_episode: null,
            demographics: {
                id: 101,
                name: 'John Smith',
                date_of_birth: moment(new Date(1980, 6, 31)),
                hospital_number: '555',
                created: moment(new Date(2015, 3, 7, 11, 45, 0)),
                age: "36",
                weight: "20.2",
                sex: null
            },
        };
    });

    describe("jsToPatient", function(){
      it("should cast date and datetime fields", function(){
          var result = FieldTranslater.jsToPatient(jsPatientData);
          expect(result.demographics).toEqual(patientData.demographics[0]);
      });

      it("should remove the spaces from around ints and floats", function(){
          jsPatientData.demographics.age = " 35 ";
          jsPatientData.demographics.weight = " 12.2 ";

          patientData.demographics[0].age = "35";
          patientData.demographics[0].weight = "12.2";
          var result = FieldTranslater.jsToPatient(jsPatientData);
          expect(result.demographics).toEqual(patientData.demographics[0]);
      });

      it("should strip episode, columnName and formController", function(){
          jsPatientData.episode = {};
          jsPatientData.columnName = "someColumnName";
          jsPatientData.formController = "someFormController";
          var result = FieldTranslater.jsToPatient(jsPatientData);
          expect(_.contains(result, "episode")).toBe(false);
          expect(_.contains(result, "columnName")).toBe(false);
          expect(_.contains(result, "formController")).toBe(false);
      });

      it('should handle single empty strings', function(){
        it("should remove the spaces from around ints and floats", function(){
            jsPatientData.demographics.age = "";
            jsPatientData.demographics.weight = "";

            patientData.demographics[0].age = undefined;
            patientData.demographics[0].weight = undefined;
            var result = FieldTranslater.jsToPatient(jsPatientData);
            expect(result.demographics).toEqual(patientData.demographics[0]);
        });
      });


      it('should handle multiple empty strings', function(){
        jsPatientData.demographics.age = "   ";
        jsPatientData.demographics.weight = "    ";

        patientData.demographics[0].age = undefined;
        patientData.demographics[0].weight = undefined;
        var result = FieldTranslater.jsToPatient(jsPatientData);
        expect(result.demographics).toEqual(patientData.demographics[0]);
      });


      it('should handle nulls', function(){
        jsPatientData.demographics.age = null;
        jsPatientData.demographics.weight = null;

        patientData.demographics[0].age = null;
        patientData.demographics[0].weight = null;
        var result = FieldTranslater.jsToPatient(jsPatientData);
        expect(result.demographics).toEqual(patientData.demographics[0]);
      })


      it('should handle strings with trailing spaces passed to dates', function(){
        jsPatientData.demographics.date_of_birth = "31/07/1980 ";
        var result = FieldTranslater.jsToPatient(jsPatientData);
        expect(result.demographics).toEqual(patientData.demographics[0]);
      });

      it('should handle strings with trailing spaces passed to date times', function(){
        jsPatientData.demographics.created = "07/04/2015 11:45:00 ";
        var result = FieldTranslater.jsToPatient(jsPatientData);
        expect(result.demographics).toEqual(patientData.demographics[0]);
      });

      it('should handle spaces  passed to dates', function(){
        jsPatientData.demographics.date_of_birth = "  ";
        patientData.demographics[0].date_of_birth = undefined;
        var result = FieldTranslater.jsToPatient(jsPatientData);
        expect(result.demographics).toEqual(patientData.demographics[0]);
      });

      it('should handle spaces  passed to date times', function(){
        jsPatientData.demographics.created = "  ";
        patientData.demographics[0].created = undefined;
        var result = FieldTranslater.jsToPatient(jsPatientData);
        expect(result.demographics).toEqual(patientData.demographics[0]);
      });
    });

    describe("patientToJs", function(){
      it("should cast date and datetime fields to moments", function(){
          var result = FieldTranslater.patientToJs(patientData);
          expect(result.id).toEqual(123);
          var dob = result.demographics[0].date_of_birth.toDate()
          expect(dob).toEqual(new Date(1980, 6, 31));

          var created = result.demographics[0].created.toDate()
          expect(created).toEqual(new Date(2015, 3, 7, 11, 45, 0));
          expect(result.demographics[0].sex).toEqual(null);
      });
    });

});
