from django.utils.translation import gettext_lazy as _

DATE = 1
DATE_PERIOD = 2
DATE_RANGE = 3
DATE_APPROXIMATED = 4
INT_DATE = 5
DATE_PHRASE = 6

DATE_VALUE_MODE = [
    (DATE, _('date')),
    (DATE_PERIOD, _('date period')),
    (DATE_RANGE, _('date range')),
    (DATE_APPROXIMATED, _('date approximated')),
    (INT_DATE, _('int date')),
    (DATE_PHRASE, _('date phrase')),
]

ABT = 1
CAL = 2
EST = 3

DATE_APPROXIMATION_MODE = [
    (ABT, _('about')), # meaning the date is not exact
    (CAL, _('calculated')), # calculated mathematically, for example, from an event date and age.
    (EST, _('estimated')), # estimated based on an algorithm using some other event date.
]

BEF = 1
AFT = 2
BTW = 3

DATE_RANGE_MODE = [
    (BEF, _('before')), # event happened before the given date
    (AFT, _('after')), # event happened after the given date.
    (BTW, _('between')), # event happened some time between date "beg" and "end"
]

OCCU = 1
EDUC = 2

WORK_EDUCATION_MODE = [
    (OCCU, _('occupation')),
    (EDUC, _('calculated')),
]

NONE= 0
UNRELI = 1
QUESTI = 2
SECOND = 3
DIRECT = 4

CONFIDENCE_MODE = [
    (NONE, _('(not specified)')),
    (UNRELI, _('unreliable evidence or estimated data')),
    (QUESTI, _('questionable reliability of evidence')),
    (SECOND, _('secondary evidence')),
    (DIRECT, _('direct and primary evidence')),
]

EVENT_TYPES = {
    'Common': ['Birth', 'Burial', 'Death', 'Education', 'Immigration', 'Nationality', 'Occupation',],
    'Birth': ['Alternate Baptism', 'Alternate Birth', 'Baby naming', 'Baptism', 'Birth', 'Circumcision', 'Misscariage',],
    'Death': ['Alternate Burial', 'Alternate Death', 'Burial', 'Commemoration', 'Cremation', 'Death', 'Funeral', 'Misscariage', 'Will', 'Will Dated', 'Will Proved',],
    'Christian': ['Adult Christening', 'Alternate Baptism', 'Alternate Christening', 'Baptism', 'Christening', 'Church', 'Confirmation', 'First Communion', 'Mission', 'Ordination',],
    'Jewish': ['Baby naming', 'Bar Mitzvah', 'Bat Mitzvah', 'Circumcision', 'Hassidism', 'Lineage', 'Pidyon haben', 'Zeved habat',],
    'Family': ['Alternate Marriage Info', 'Anecdote', 'Annulment', 'Civil Marriage', 'Comment', 'Divorce', 'Divorce filed', 'Engagement', 'Fact 1', 'Fact 2', 'Fact 3', 'Fact 4', 'Fact 5', 'Fact 6', 'Fact 7', 'Fact 8', 'Fact 9', 'Family Address', 'Friends', 'Known Number of Children', 'Marriage', 'Marriage Bann', 'Marriage contract', 'Marriage License', 'Marriage Settlement', 'Misc', 'Partners', 'Separation', 'Unknown',],
    'Residence': ['Census', 'Emigration', 'Immigration', 'Move', 'Nationality', 'Naturalization', 'Passenger list', 'Settlement',],
    'Legal': ['Census', 'Crime', 'Deed', 'Election', 'ID Number', 'Nationality', 'Naturalization', 'Probate', 'Property', 'Social Security Number', 'Will', 'Will Dated', 'Will Proved',],
    'Education': ['Award', 'Degree', 'Education', 'Graduation',],
    'Military': ['Military Award', 'Military Discharge', 'Military Enlistment', 'Military Promotion', 'Military Service',],
    'Personal history': ['Accomplishment', 'Association', 'Award', 'Deed', 'Degree', 'Education', 'Employer', 'Family Reunion', 'Graduation', 'Hospitalization', 'Illness', 'Known Number of Children', 'Known Number of Marriages', 'Membership', 'Name Change', 'Named after', 'Occupation', 'Personality and Interests', 'Retirement',],
    'General': ['Anecdote', 'Comment', 'Fact 1', 'Fact 2', 'Fact 3', 'Fact 4', 'Fact 5', 'Fact 6', 'Fact 7', 'Fact 8', 'Fact 9', 'Misc',],
    'All facts': [],
}

UNKN_PL = 0
ADOP_PL = 1
BIRT_PL = 2
FOST_PL = 3
# SEAL_PL = 4

PEDIGREE_LINK_MODE = [
    (UNKN_PL, _('-------')),   # unknown
    (ADOP_PL, _('adopted')),   # indicates adoptive parents
    (BIRT_PL, _('birth')),     # indicates birth parents
    (FOST_PL, _('foster')),    # indicates child was included in a foster or guardian family
    # (SEAL_PL, _('sealing')),   # indicates child was sealed to parents other than birth parents
]

CHAL_CL = 1
DISP_CL = 2
PROV_CL = 3

# A status code that allows passing on the users opinion of the status of a child to family link.
CHILD_LINK_MODE = [
    (CHAL_CL, _('challenged')), # linking this child to this family is suspect, but the linkage has been neither proven nor disproven
    (DISP_CL, _('disproven')),  # there has been a claim by some that this child belongs to this family, but the linkage has been disproven
    (PROV_CL, _('proven')),     # there has been a claim by some that this child does not belongs to this family, but the linkage has been proven
]

# Object type fo Media record
MO_SOURCE = 1
MO_PERS = 2
MO_FAMI = 3
MO_PERS_FACT = 4
MO_FAMI_FACT = 5
MO_CITAT = 6

COUNTRIES = [
    ('Литва', 'Литва'),
    ('Белоруссия', 'Беларусь'),
    ('Беларусь', 'Беларусь'),
    ('BY', 'Беларусь'),
    ]

CITIES = [
    ('Вільнюс', 'Вильнюс'),
    ('г. Жодина', 'Жодино'),
    ('г.Жодина', 'Жодино'),
    ('Жодино', 'Жодино'),
    ('г. Волковыск', 'Волковыск'),
    ('г.Волковыск', 'Волковыск'),
    ('г.Волковыск.', 'Волковыск'),
    ('г. Минск', 'Минск'),
    ('г.Минск', 'Минск'),
    ('Г Минск', 'Минск'),
    ('Минск', 'Минск'),
    ('Липецкая обл.,с.Боринское', 'Липецкая обл., с.Боринское'),
    ('г. Брест', 'Брест'),
    ]

STREETS = [
    'ул.Дзержинского, д.55', 
    'ул.Якубова, д.66 , к.1, кв.207', 
    ]

POSTS = [
    '220116', 
    '220095', 
    ]

LITERS = {
    'HEAD': 'H',
    'FAM':  'F',
    'INDI': 'I',
    'OBJE': 'M',
    'NOTE': 'N',
    'REPO': 'R',
    'SOUR': 'S',
    'SUBM': 'U',
    '_ALBUM': 'A',
}

PEDI_SELECT   = [('birth', _('birth')), ('adopted', _('adopted')), ('foster', _('foster'))]
PARENT_RELAT_SELECT   = [
    ('his_father', _('his father').capitalize()), 
    ('his_mother', _('his mother').capitalize()),
    ('her_father', _('her father').capitalize()), 
    ('her_mother', _('her mother').capitalize()),
]

