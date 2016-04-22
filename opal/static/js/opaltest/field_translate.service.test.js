describe('services', function() {
    "use strict";

    var $rootScope, FieldTranslater, patientData;

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
                created: "07/04/2015 11:45:00"
            }],
        };


    });

    it("should cast to fields", function(){
        var result = FieldTranslater.patientToJs(patientData);
        expect(result.id).toEqual(123);
        var dob = result.demographics[0].date_of_birth.toDate()
        expect(dob).toEqual(new Date(1980, 6, 31));
    });
});
