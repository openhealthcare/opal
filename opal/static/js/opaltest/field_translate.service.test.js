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
                sex: null
            },
        };
    });

    describe("jsToPatient", function(){
      it("should cast date and datetime fields", function(){
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
