"""
Define the patient flows for our system
"""

flows = {
    'default': {
        'enter': {
            'controller': 'HospitalNumberCtrl',
            'template'  : '/templates/modals/hospital_number.html/'
        },
        'exit': {
            'controller': 'DischargeEpisodeCtrl',
            'template'  : '/templates/modals/discharge_episode.html/'
        }
    }
}
