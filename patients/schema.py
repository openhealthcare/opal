from patients import models

columns = [
    models.Demographics,
    models.Location,
    models.Diagnosis,
    models.PastMedicalHistory,
    models.Travel,
    models.Antimicrobial,
    models.MicrobiologyTest,
    models.MicrobiologyInput,
    models.GeneralNote,
    models.Todo,
]

detail_columns = [
    models.Demographics,
    models.Diagnosis,
    models.PastMedicalHistory,
    models.MicrobiologyInput,
    models.MicrobiologyTest,
    models.Antimicrobial,
    models.Travel,
    models.Todo,
    models.Location,
    models.GeneralNote,
]
