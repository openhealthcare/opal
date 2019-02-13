controllers.controller(
    'PatientRecordAccessLogCtrl',
    function($scope, $rootScope, $http, patient){
        $scope.patient = patient;

        $http.get('/api/v0.1/patientrecordaccess/' + patient.id + '/').then(
            function(response){
                $scope.access_log = response.data;
                $rootScope.state = 'normal'
            }
        )

});
