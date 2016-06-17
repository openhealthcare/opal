// TODO make this a service
var CATEGORIES = [
    'Inepisode', 'Review', 'Followup', 'Transferred', 'Discharged', 'Deceased'
];

var records = OPAL.module('opal.records', [])

var services = OPAL.module('opal.services', [
    'ngResource',
    'ngRoute',
    'ui.bootstrap',
    'opal.records'
]);
