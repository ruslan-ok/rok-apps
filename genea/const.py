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

"""
# Person fact categories
COMM = 1 # Common
BIRT = 2 # Birth
DEAT = 3 # Death
CRIS = 4 # Cristian
JEWI = 5 # Jewish
FAMI = 6 # Family
RESI = 7 # Residence
LEGA = 8 # Legal
EDUC = 9 # Education
MILI = 10 # Military
HIST = 11 # Personal history
GENE = 12 # General
ALLF = 13 # All facts
"""

MARR = 1
DIVO = 2
SEPA = 3
WIDO = 4
ENGA = 5
PRTN = 6
FRIE = 7
ANNU = 8
UNKN = 9
OTHE = 10

RELATIONSHIP_MODE = [
    (MARR, _('married')),
    (DIVO, _('divorced')),
    (SEPA, _('separated')),
    (WIDO, _('widowed')),
    (ENGA, _('engaged')),
    (PRTN, _('partner')),
    (FRIE, _('friends')),
    (ANNU, _('annulment')),
    (UNKN, _('unknown')),
    (OTHE, _('other')),
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
    'Family': ['Alternate Marriage Info', 'Anecdote', 'Annulment', 'Civil Marriage', 'Comment', 'Divorce', 'Divorce filed', 'Engagement', 'Fact 1', 'Fact 2', 'Fact 3', 'Fact 4', 'Fact 5', 'Fact 6', 'Fact 7', 'Fact 8', 'Fact 9', 'Family Address', 'Friends', 'Known Number of Children', 'Marriage', 'Marriage Bann', 'Marriage contract', 'Marriage Settlement', 'Misc', 'Partners', 'Separation', 'Unknown',],
    'Residence': ['Census', 'Emigration', 'Immigration', 'Move', 'Nationality', 'Naturalization', 'Passenger list', 'Settlement',],
    'Legal': ['Census', 'Crime', 'Deed', 'Election', 'ID Number', 'Nationality', 'Naturalization', 'Probate', 'Property', 'Social Security Number', 'Will', 'Will Dated', 'Will Proved',],
    'Education': ['Award', 'Degree', 'Education', 'Graduation',],
    'Military': ['Military Award', 'Military Discharge', 'Military Enlistment', 'Military Promotion', 'Military Service',],
    'Personal history': ['Accomplishment', 'Association', 'Award', 'Deed', 'Degree', 'Education', 'Employer', 'Family Reunion', 'Graduation', 'Hospitalization', 'Illness', 'Known Number of Children', 'Known Number of Marriages', 'Membership', 'Name Change', 'Named after', 'Occupation', 'Personality and Interests', 'Retirement',],
    'General': ['Anecdote', 'Comment', 'Fact 1', 'Fact 2', 'Fact 3', 'Fact 4', 'Fact 5', 'Fact 6', 'Fact 7', 'Fact 8', 'Fact 9', 'Misc',],
    'All facts': [],
}
