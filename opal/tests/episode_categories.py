from opal.core.episodes import EpisodeCategory


class InpatientEpisode(EpisodeCategory):
    display_name    = 'Inpatient'
    detail_template = 'detail/inpatient.html'
    stages          = [
        'Inpatient',
        'Followup',
        'Discharged'
    ]
