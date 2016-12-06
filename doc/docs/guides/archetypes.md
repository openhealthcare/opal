# Core Clinical Archetypes

Opal ships with a wide range of core clinical concepts implemented as Abstract Subrecords.
Applications that are generated via the `$ opal startproject` command will automatically
contain concrete implementations of these models in the application.

## Common Metadata fields

All subrecords will contain the following fields, which are not repreated individually


Field|Type|Length
-----|----|---
created_by | FK | User ID
created | Date
updated_by | FK User ID
update | Date

The details of each individual archetype are set out below:

## Patient Subrecords

### Demographics

Field|Type|Length
-----|----|---
hospital_number|Char|255
nhs_number|Char|255
date_of_birth|Date|
place_of_birth| FKorFT(Destination)
ethnicity|FKorFT(Ethnicity)
surname | Char| 255
first_name | Char| 255
middle_name | Char| 255
sex| FKorFT(Gender)

### Allergies

Field|Type|Length
-----|----|---
drug | FKorFT(Drug)
provisional | Boolean
details | Char|255


## Episode Subrecords

### Location

Field|Type|Length
-----|----|---
category | Char | 255
hospital | Char| 255
ward | Char | 255
bed | Char | 255

### Treatment

Field|Type|Length
-----|----|---
drug | FKorFT(Drug) |
dose | Char | 255
route | FKorFT(Drugroute)
start_date | Date
end_date | Date
frequency | FKorFT(Drugfreq)

### Diagnosis

Field|Type|Length
-----|----|---
condition | FKorFT(Condition)
provisional | Boolean
details | Char | 255
date_of_diagnosis | Date

### PastMedicalHistory

Field|Type|Length
-----|----|---
condition | FKorFT(Condition)
year | Char | 4
details | Char | 255

### SymptomComplex

Field|Type|Length
-----|----|---
symptoms | ManyToMany(Symptom)
duration | Char | 255
details | Text

### ReferralRoute

Field|Type|Length
-----|----|---
internal | NullBoolean
referral_route | FKorFT(ReferralOrganisation)
referral_name | Char | 255
date_of_referral | Date
referral_team | FKorFT(Speciality)
referral_reason | FKorFT(ReferralReason)

### PatientConsultation

Field|Type|Length
-----|----|---
when | Datetime
initials | Char | 255
reason_for_interaction | FKorFT(Patient_consultation_reason_for_interaction)
discussion | Text

### Investigation

Field|Type|Length
-----|----|---
test                  | Char |255
date_ordered          | Date
details               | Char |255
microscopy            | Char |255
organism              | Char |255
sensitive_antibiotics | Char |255
resistant_antibiotics | Char |255
result                | Char |255
igm                   | Char |20
igg                   | Char |20
vca_igm               | Char |20
vca_igg               | Char |20
ebna_igg              | Char |20
hbsag                 | Char |20
anti_hbs              | Char |20
anti_hbcore_igm       | Char |20
anti_hbcore_igg       | Char |20
rpr                   | Char |20
tppa                  | Char |20
viral_load            | Char |20
parasitaemia          | Char |20
hsv                   | Char |20
vzv                   | Char |20
syphilis              | Char |20
c_difficile_antigen   | Char |20
c_difficile_toxin     | Char |20
species               | Char |20
hsv_1                 | Char |20
hsv_2                 | Char |20
enterovirus           | Char |20
cmv                   | Char |20
ebv                   | Char |20
influenza_a           | Char |20
influenza_b           | Char |20
parainfluenza         | Char |20
metapneumovirus       | Char |20
rsv                   | Char |20
adenovirus            | Char |20
norovirus             | Char |20
rotavirus             | Char |20
giardia               | Char |20
entamoeba_histolytica | Char |20
cryptosporidium       | Char |20
