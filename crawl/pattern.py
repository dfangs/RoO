"""
pattern.py
Author: Dean Fanggohans
Last modified: 04:11 EST, November 27, 2019

Contains defined constants and patterns related to Rules of Origin, as well as
user-defined Pattern class (to capture each specific type rule).
"""

import regex

## -----------------------------------------------------------------------------
## Constants
## -----------------------------------------------------------------------------

# Detect entire HS code (including tariff item)
HS_CODE_FULL = r'(?<!\.)\b(\d{2,4}\.?\d{2}\b(?:\.\w+)?)'
HS_CODE_FULL_NC = r'(?<!\.)\b(?:\d{2,4}\.?\d{2}\b(?:\.\w+)?)'

# Detect tariff item, but only capture up to 6 digits, excluding chapter
HS_CODE_8 = r'(?<!\.)\b(\d{2,4}\.?\d{2})\b(?:\.\w+)?'
HS_CODE_8_NC = r'(?<!\.)\b(?:\d{2,4}\.?\d{2})\b(?:\.\w+)?'
# Detect up to 6 digits, excluding chapter
HS_CODE_6 = r'(?<!\.)\b(\d{2,4}\.?\d{2})\b(?!\.\w)'
HS_CODE_6_NC = r'(?<!\.)\b(?:\d{2,4}\.?\d{2})\b(?!\.\w)'
# Detect only 2 digits (chapter)
CH_NUMBER = r'(?<!\.)\b(\d\d?)\b(?!\.\d)'
CH_NUMBER_NC = r'(?<!\.)\b(?:\d\d?)\b(?!\.\d)'

# Group of HS codes (up to tariff item); note the hyphen/en dash
# Rename if possible?
HSC_GROUP_8 = r'({0}(?:\-{0})?)'.format(HS_CODE_FULL)
HSC_GROUP_8_NC = r'{0}(?:\-{0})?'.format(HS_CODE_FULL_NC)
# Available tiers in Harmonized System
HS_TIER = r'([Cc]hapter|heading|subheading|tariff item)s?'
HS_TIER_NC = r'(?:[Cc]hapter|heading|subheading|tariff item)s?'

# Capture both group of chapters and group of HS codes (up to tariff item); note the absent of tier
CH_HSC_RANGE_8 = r'(?:{0}(?: through {0})?|{1}(?: through(?: {2})? {1})?)'.format(CH_NUMBER, HS_CODE_8, HS_TIER_NC)
CH_HSC_RANGE_8_NC = r'(?:{0}(?: through {0})?|{1}(?: through(?: {2})? {1})?)'.format(CH_NUMBER_NC, HS_CODE_8_NC, HS_TIER_NC)
# Capture both group of chapters and group of HS codes (up to 6 digits); note the absent of tier
CH_HSC_RANGE_6 = r'(?:{0}(?: through {0})?|{1}(?: through(?: {2})? {1})?)'.format(CH_NUMBER, HS_CODE_6, HS_TIER_NC)
CH_HSC_RANGE_6_NC = r'(?:{0}(?: through {0})?|{1}(?: through(?: {2})? {1})?)'.format(CH_NUMBER_NC, HS_CODE_6_NC, HS_TIER_NC)

# Used only in the beginning of clause, e.g. "A change to ..." (hence no chapter, and up to tariff item)
HSC_RANGE_8 = r'(?:heading|subheading|tariff item)s? {0}(?: through {0})?'.format(HS_CODE_FULL)
HSC_RANGE_8_NC = r'(?:heading|subheading|tariff item)s? {0}(?: through {0})?'.format(HS_CODE_FULL_NC)

# Multiple group of HS codes
# Note: This works partly because in the actual patterns, '\.' is always followed by '$',
#       thus making it always looking for the end (without stopping at the HS' dot)
# Doesn't matter if it's greedy? -> Confirmed
MULTI = r'((?:[^;](?!provided th|except from|A change))+?)'
MULTI_NC = r'(?:[^;](?!provided th|except from|A change))+?'

# Optional phrase to disambiguate between normal CTC and CTC_OTG
INCLUDE = r'(?:, including(?: from)? another {0} within (?:that group|{1}))?'.format(HS_TIER_NC, HSC_RANGE_8_NC)

# Basic RoO types
CTC = r'A change to(?: a good of)? {0} from any other {1}{2}'.format(HSC_RANGE_8_NC, HS_TIER, INCLUDE)
CTC_OTG = r'A change to(?: a good of)? {0} from any(?: other)? {1} outside that group'.format(HSC_RANGE_8_NC, HS_TIER)
CTC_ECT = r'A change to(?: a good of)? {0} from any other {1}{2},? except from {3}'.format(HSC_RANGE_8_NC, HS_TIER, INCLUDE, MULTI)
CTC_OTG_ECT = r'A change to(?: a good of)? {0} from any(?: other)? {1} outside that group,? except from {2}'.format(HSC_RANGE_8_NC, HS_TIER, MULTI)
# Consider using separate MULTI? (originally MULTI has no 'except from')
CTC_MULTI_1 = r'A change to(?: a good of)? {0} from {1} or any other {2}'.format(HSC_RANGE_8_NC, MULTI, HS_TIER)
CTC_MULTI_1_ECT = r'A change to(?: a good of)? {0} from {1} or any other {2},? except from {3}'.format(HSC_RANGE_8_NC, MULTI, HS_TIER, MULTI)
CTC_MULTI_2 = r'A change to(?: a good of)? {0} from any other {2} or from {1}'.format(HSC_RANGE_8_NC, MULTI, HS_TIER)
CTC_MULTI_2_ECT = r'A change to(?: a good of)? {0} from any other {2} or from {1},? except from {3}'.format(HSC_RANGE_8_NC, MULTI, HS_TIER, MULTI)

# VA requirement
RVC_TYPE_NC = r'(?:[Bb]uild-?down|[Bb]uild-?up|transaction value|[Nn]et [Cc]ost|focused value)'
RVC_CLAUSE_NC = r'(?: (?:under|based on) the {0} method(?: taking into account [\w\W]+?)?| (?:when|where) the {0} method is used)?'.format(RVC_TYPE_NC)
RVC = r'provided(?: that)? there is(?: also)?(?: a)? (?:qualifying|regional) value content of not less than(?:\: (?:[Aa]\.|\([Aa]\)))? (\d\d?) per\s?cent{0}(?:[;,]?(?: or)?(?: [Bb]\.| \([Bb]\)| of not less than)? (\d\d?) per\s?cent{0})?(?:[;,] or (?:[Cc]\.|\([Cc]\)) (\d\d?) per\s?cent{0})?'.format(RVC_CLAUSE_NC)

# No required CTC; special alternative clause
NO_CTC = r'No(?: required)? change in tariff classification(?: (?:to(?: any of)?|required for a good of)? {0})?(?: is required)?'.format(HSC_RANGE_8_NC)

# Double-clause / alternative clause
# Consider merging the first multi and 'whether' clause?
CTC_ALT = r'A change to(?: a good of)? ({0}) from {1}(?:, whether or not {2})?'.format(HSC_RANGE_8_NC, MULTI, MULTI_NC)

# Technical requirement (non-RVC)
MFT_NC = r'provided th(?:[\w\W](?!(?:qualifying|regional) value content|; or (?:A change|No)))+?'

## -----------------------------------------------------------------------------
## Patterns
## -----------------------------------------------------------------------------

raw_patterns = {
    'CTC': r'^{0}\.$'.format(CTC),
    'CTCo': r'^{0}\.$'.format(CTC_OTG),
    'CTCe': r'^{0}\.$'.format(CTC_ECT),
    'CTCoe': r'^{0}\.$'.format(CTC_OTG_ECT),
    'CTCm1': r'^{0}\.$'.format(CTC_MULTI_1),
    'CTCm1e': r'^{0}\.$'.format(CTC_MULTI_1_ECT),
    'CTCm2': r'^{0}\.$'.format(CTC_MULTI_2),
    'CTCm2e': r'^{0}\.$'.format(CTC_MULTI_2_ECT),

    'RVC': r'^{0},? {1}\.$'.format(NO_CTC, RVC),

    'CTC+RVC': r'^{0},? {1}\.$'.format(CTC, RVC),
    'CTCo+RVC': r'^{0},? {1}\.$'.format(CTC_OTG, RVC),
    'CTCe+RVC': r'^{0},? {1}\.$'.format(CTC_ECT, RVC),
    'CTCoe+RVC': r'^{0},? {1}\.$'.format(CTC_OTG_ECT, RVC),
    'CTCm1+RVC': r'^{0},? {1}\.$'.format(CTC_MULTI_1, RVC),
    'CTCm1e+RVC': r'^{0},? {1}\.$'.format(CTC_MULTI_1_ECT, RVC),
    'CTCm2+RVC': r'^{0},? {1}\.$'.format(CTC_MULTI_2, RVC),
    'CTCm2e+RVC': r'^{0},? {1}\.$'.format(CTC_MULTI_2_ECT, RVC),

    # Inconsistencies of using comma or semicolon
    'CTC_or_RVC': r'^{0}[;,] or {1},? {2}\.$'.format(CTC, NO_CTC, RVC),
    'CTCo_or_RVC': r'^{0}[;,] or {1},? {2}\.$'.format(CTC_OTG, NO_CTC, RVC),
    'CTCe_or_RVC': r'^{0}[;,] or {1},? {2}\.$'.format(CTC_ECT, NO_CTC, RVC),
    'CTCoe_or_RVC': r'^{0}[;,] or {1},? {2}\.$'.format(CTC_OTG_ECT, NO_CTC, RVC),
    'CTCm1_or_RVC': r'^{0}[;,] or {1},? {2}\.$'.format(CTC_MULTI_1, NO_CTC, RVC),
    'CTCm1e_or_RVC': r'^{0}[;,] or {1},? {2}\.$'.format(CTC_MULTI_1_ECT, NO_CTC, RVC),
    'CTCm2_or_RVC': r'^{0}[;,] or {1},? {2}\.$'.format(CTC_MULTI_2, NO_CTC, RVC),
    'CTCm2e_or_RVC': r'^{0}[;,] or {1},? {2}\.$'.format(CTC_MULTI_2_ECT, NO_CTC, RVC),

    'CTC1_or_CTC2m+RVC': r'^{0}; or {1},? {2}\.$'.format(CTC, CTC_ALT, RVC),
    'CTC1o_or_CTC2m+RVC': r'^{0}; or {1},? {2}\.$'.format(CTC_OTG, CTC_ALT, RVC),
    'CTC1e_or_CTC2m+RVC': r'^{0}; or {1},? {2}\.$'.format(CTC_ECT, CTC_ALT, RVC),
    'CTC1oe_or_CTC2m+RVC': r'^{0}; or {1},? {2}\.$'.format(CTC_OTG_ECT, CTC_ALT, RVC),
    'CTC1m1_or_CTC2m+RVC': r'^{0}; or {1},? {2}\.$'.format(CTC_MULTI_1, CTC_ALT, RVC),
    'CTC1m1e_or_CTC2m+RVC': r'^{0}; or {1},? {2}\.$'.format(CTC_MULTI_1_ECT, CTC_ALT, RVC),
    'CTC1m2_or_CTC2m+RVC': r'^{0}; or {1},? {2}\.$'.format(CTC_MULTI_2, CTC_ALT, RVC),
    'CTC1m2e_or_CTC2m+RVC': r'^{0}; or {1},? {2}\.$'.format(CTC_MULTI_2_ECT, CTC_ALT, RVC),

    'CTC+MFT': r'^{0},? {1}\.$'.format(CTC, MFT_NC),
    'CTCo+MFT': r'^{0},? {1}\.$'.format(CTC_OTG, MFT_NC),
    'CTCe+MFT': r'^{0},? {1}\.$'.format(CTC_ECT, MFT_NC),
    'CTCoe+MFT': r'^{0},? {1}\.$'.format(CTC_OTG_ECT, MFT_NC),
    'CTCm1+MFT': r'^{0},? {1}\.$'.format(CTC_MULTI_1, MFT_NC),
    'CTCm1e+MFT': r'^{0},? {1}\.$'.format(CTC_MULTI_1_ECT, MFT_NC),
    'CTCm2+MFT': r'^{0},? {1}\.$'.format(CTC_MULTI_2, MFT_NC),
    'CTCm2e+MFT': r'^{0},? {1}\.$'.format(CTC_MULTI_2_ECT, MFT_NC),

    # Need to refine the first multi {0}
    'CTCr': r'^A change to {0} from {0} or any other {1}; or A change to {0} from(?: {0} or)? any other {2}\.$'.format(MULTI_NC, HS_TIER, HS_TIER_NC)
}

categories = {
    # Handle MUL, need check
    'CTC': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTCo': {'CTC': True, 'OTG': True, 'ECT': False, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTCe': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTCoe': {'CTC': True, 'OTG': True, 'ECT': True, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTCm1': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': True, 'MUL2': False},
    'CTCm1e': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': True, 'MUL2': False},
    'CTCm2': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': True},
    'CTCm2e': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': True},

    'RVC': {'CTC': False, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': False},

    # Set CVA to False to match Conconi et al.
    'CTC+RVC': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': True, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTCo+RVC': {'CTC': True, 'OTG': True, 'ECT': False, 'EXM': False, 'CVA': True, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTCe+RVC': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': False, 'CVA': True, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTCoe+RVC': {'CTC': True, 'OTG': True, 'ECT': True, 'EXM': False, 'CVA': True, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTCm1+RVC': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': True, 'AVA': False, 'MUL1': True, 'MUL2': False},
    'CTCm1e+RVC': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': False, 'CVA': True, 'AVA': False, 'MUL1': True, 'MUL2': False},
    'CTCm2+RVC': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': True, 'AVA': False, 'MUL1': False, 'MUL2': True},
    'CTCm2e+RVC': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': False, 'CVA': True, 'AVA': False, 'MUL1': False, 'MUL2': True},

    'CTC_or_RVC': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': False, 'AVA': True, 'MUL1': False, 'MUL2': False},
    'CTCo_or_RVC': {'CTC': True, 'OTG': True, 'ECT': False, 'EXM': False, 'CVA': False, 'AVA': True, 'MUL1': False, 'MUL2': False},
    'CTCe_or_RVC': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': False, 'CVA': False, 'AVA': True, 'MUL1': False, 'MUL2': False},
    'CTCoe_or_RVC': {'CTC': True, 'OTG': True, 'ECT': True, 'EXM': False, 'CVA': False, 'AVA': True, 'MUL1': False, 'MUL2': False},
    'CTCm1_or_RVC': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': False, 'AVA': True, 'MUL1': True, 'MUL2': False},
    'CTCm1e_or_RVC': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': False, 'CVA': False, 'AVA': True, 'MUL1': True, 'MUL2': False},
    'CTCm2_or_RVC': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': False, 'AVA': True, 'MUL1': False, 'MUL2': True},
    'CTCm2e_or_RVC': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': False, 'CVA': False, 'AVA': True, 'MUL1': False, 'MUL2': True},

    'CTC1_or_CTC2m+RVC': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': True, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTC1o_or_CTC2m+RVC': {'CTC': True, 'OTG': True, 'ECT': False, 'EXM': True, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTC1e_or_CTC2m+RVC': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': True, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTC1oe_or_CTC2m+RVC': {'CTC': True, 'OTG': True, 'ECT': True, 'EXM': True, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTC1m1_or_CTC2m+RVC': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': True, 'CVA': False, 'AVA': False, 'MUL1': True, 'MUL2': False},
    'CTC1m1e_or_CTC2m+RVC': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': True, 'CVA': False, 'AVA': False, 'MUL1': True, 'MUL2': False},
    'CTC1m2_or_CTC2m+RVC': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': True, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': True},
    'CTC1m2e_or_CTC2m+RVC': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': True, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': True},

    'CTC+MFT': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTCo+MFT': {'CTC': True, 'OTG': True, 'ECT': False, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTCe+MFT': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTCoe+MFT': {'CTC': True, 'OTG': True, 'ECT': True, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': False},
    'CTCm1+MFT': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': True, 'MUL2': False},
    'CTCm1e+MFT': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': True, 'MUL2': False},
    'CTCm2+MFT': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': True},
    'CTCm2e+MFT': {'CTC': True, 'OTG': False, 'ECT': True, 'EXM': False, 'CVA': False, 'AVA': False, 'MUL1': False, 'MUL2': True}

    #'CTCr': {'CTC': True, 'OTG': False, 'ECT': False, 'EXM': False, 'CVA': False, 'MUL': False},
}

## -----------------------------------------------------------------------------
## Class Definition
## -----------------------------------------------------------------------------

class Pattern:
    """Represent a type of RoO; encapsulate the regular expression (regex) pattern
    along with relevant methods for interpreting the rules.

    Methods:
      search():
        Classify a rule of origin, and return a preliminary set of restrictions
        corresponding to range of HS codes imposed by the rule.
      finalize():
        Invoke after search(); finalize all restrictions corresponding to a
        six-digit HS code output product.
      check():
        Only classify the rule without additional processing.
    """
    # Class variables
    PATTERN_RANGE = regex.compile(CH_HSC_RANGE_6)
    PATTERN_SELF_ANTIEXEMPT = regex.compile(r'any other {0} within'.format(HS_TIER))
    PATTERN_EXEMPT_TO = regex.compile(HSC_RANGE_8)

    def __init__(self, name, pattern, category=None):
        """Initialize an instance of Pattern.

        Inputs:
          `name`: string representing the type of RoO
          `pattern`: raw string (i.e. r'') of regular expression
          `category`: dict containing the labels of RoO
        """
        self.name = name
        self.pattern = regex.compile(pattern)
        if category:
            self.change = category['CTC']
            self.group = category['OTG']
            self.exception = category['ECT']
            self.exemption = category['EXM']
            self.comp_va = category['CVA']
            self.alt_va = category['AVA']
            self.multi_1 = category['MUL1']
            self.multi_2 = category['MUL2']
            self.indices = self.get_indices()

    def search(self, hs_codes, rule, hs_map):
        """Return a set of (almost all) restrictions imposed by single rule of origin,
        along with a dictionary containing information which `finalize()` can handle.

        Inputs:
          `hs_codes`: list of HS codes affected by `rule`
          `rule`: string containing the rule of origin
          `hs_map`: instance of HSMap used to decipher the rule

        Output:
        (restrictions, exemptions, toHandle)
        `restrictions`: set of unique HS codes restricted according to `rule`
        `exemptions`: set of unique HS codes "exempted" due to Value Added rules
        `toHandle`: dictionary to be handled by finalize()
        """
        # In general, beware of search(): unlike findall(), it might accidentally return None instead of ''
        match = self.pattern.search(rule)
        if match:
            restrictions, toHandle = {}, {}

            if self.change:
                digits = self.classify(match[self.indices['CTC']])
                if self.group:
                    restrictions.update(self.get_restrictions(hs_codes, digits, hs_map))
                else:
                    toHandle['OTG'] = digits

            if self.exception:
                restrictions.update(self.get_exceptions(match[self.indices['ECT']], hs_map))

            if self.exemption:
                RVC_0 = Pattern.calculate_rvc(match, self.indices['RVC'])
                exemptions_to = self.get_exemptions_to(match[self.indices['EXM_t']], hs_map)
                exemptions_from = self.get_exemptions_from(match[self.indices['EXM_f']], RVC_0, hs_codes, hs_map)

                # Cancel exemption of self within specific HS code
                # Note: Could refine the constant
                self_antiexempt = Pattern.PATTERN_SELF_ANTIEXEMPT.search(match[self.indices['EXM_f']])
                exempt_digits = self.classify(self_antiexempt[1]) if self_antiexempt else None

                toHandle['EXM'] = (exemptions_to, exemptions_from, exempt_digits)

            if self.comp_va or self.alt_va:
                toHandle['RVC'] = Pattern.calculate_rvc(match, self.indices['RVC'])

            # Distinguish between MULTI and RVC, Multi = green, exempt = yellow
            # Consider merging the handler, or make a separate handler for multi
            if self.multi_1 or self.multi_2:
                # Handle because this must be processed after `restrictions`
                toHandle['MUL'] = self.get_exemptions_from(match[self.indices['MUL']], 0, hs_codes, hs_map)

            return restrictions, toHandle

        else:
            return None

    def finalize(self, hs_code, result, hs_map):
        """Return a list of tuples containing restriction data corresponding to an output product.

        Inputs:
          `hs_code`: string of HS code
          `result`: string containing the rule of origin
          `hs_map`: instance of HSMap used to decipher the rule

        Output:
        `restrictions`: list of tuples (HS code, restrictiveness), where HS code in the tuple
                        represents an input product, and restrictiveness scales from 0 to 1,
                        with 1 representing pure CTC and <1 representing VA requirement percentage
        """
        restrictions, toHandle = result
        exemptions = {}

        if 'OTG' in toHandle:
            digits = toHandle['OTG']
            restrictions = {**restrictions, **self.get_restrictions([hs_code], digits, hs_map)}

        if 'EXM' in toHandle:
            exemptions_to, exemptions_from, exempt_digits = toHandle['EXM']
            if hs_code in exemptions_to:
                exemptions = exemptions_from.copy()
                if exempt_digits:
                    for hs_code_ in hs_map.get_hs_codes(hs_code[:exempt_digits]):
                        del exemptions[hs_code_]

        if 'MUL' in toHandle:
            restrictions = {**restrictions, **toHandle['MUL']}

        # Ordering: pure VA should be last
        # Mutually exclusive with exemptions

        ## Not included to match Conconi et al.'s approach
        # if self.comp_va:
        #    complement = set(hs_map.get_all_hs_codes()) - set(restrictions)
        #    restrictions = {**restrictions, **{hs_code_: toHandle['RVC'] for hs_code_ in complement}}

        if self.alt_va:
            restrictions = {**restrictions, **{hs_code_: toHandle['RVC'] for hs_code_ in restrictions}}

        return {**restrictions, **exemptions}

    def get_indices(self):
        """Return indices corresponding to each particular type of regex group."""
        indices = {}
        if self.change:
            if self.multi_1 or self.multi_2:
                indices['CTC'] = 2 if self.multi_1 else 1
                indices['MUL'] = 1 if self.multi_1 else 2
                if self.exception:
                    indices['ECT'] = 3
                if self.exemption:
                    indices['EXM_t'] = 4 if self.exception else 3
                    indices['EXM_f'] = 5 if self.exception else 4
            else:
                indices['CTC'] = 1
                if self.exception:
                    indices['ECT'] = 2
                if self.exemption:
                    indices['EXM_t'] = 3 if self.exception else 2
                    indices['EXM_f'] = 4 if self.exception else 3

        indices['RVC'] = len(indices) + 1
        return indices

    def check(self, rule):
        """Check if `rule` belongs to this type of RoO (Pattern)."""
        if self.pattern.search(rule):
            return True
        return False

    @staticmethod
    def classify(tier):
        """Classify tier and return corresponding number of digits."""
        if tier == 'chapter':
            digits = 2
        elif tier == 'heading':
            digits = 4
        elif tier == 'subheading' or tier == 'tariff item':
            digits = 6
        else:
            raise ValueError
        return digits

    @staticmethod
    def calculate_rvc(match, index):
        "From 3 (max) possible RVC values, return the lowest one."""
        RVCs = []
        for i in range(index, len(match.groups()) + 1):
            if match[i]:
                RVCs.append(int(match[i]))
        return min(RVCs) / 100

    @staticmethod
    def get_restrictions(hs_codes, digits, hs_map):
        """Handler function for 'CTC' label."""
        restrictions = {}
        unique_levels = set([hs_code[:digits] for hs_code in hs_codes])
        for unique_hs in unique_levels:
            restrictions.update({hs_code: 1.0 for hs_code in hs_map.get_hs_codes(unique_hs)})
        return restrictions

    @staticmethod
    def get_exceptions(clause, hs_map):
        """Handler function for 'ECT' label."""
        exceptions = {}
        for ch_1, ch_2, hs_code1, hs_code2 in Pattern.PATTERN_RANGE.findall(clause):
            if ch_1:
                ch_1, ch_2 = ch_1.zfill(2), ch_2.zfill(2) if ch_2 else ch_2
                exceptions.update({hs_code: 1.0 for hs_code in hs_map.get_hs_codes(ch_1, ch_2)})
            else:
                exceptions.update({hs_code: 1.0 for hs_code in hs_map.get_hs_codes(hs_code1, hs_code2)})
        return exceptions

    @staticmethod
    def get_exemptions_to(phrase, hs_map):
        hs_code1, hs_code2 = Pattern.PATTERN_EXEMPT_TO.findall(phrase)[0]
        return set(hs_map.get_hs_codes(hs_code1, hs_code2))

    @staticmethod
    def get_exemptions_from(clause, RVC_0, hs_codes, hs_map):
        """Handler function for 'EXM' label."""
        exemptions = {}
        for ch_1, ch_2, hs_code1, hs_code2 in Pattern.PATTERN_RANGE.findall(clause):
            if ch_1:
                ch_1, ch_2 = ch_1.zfill(2), ch_2.zfill(2) if ch_2 else ch_2
                exemptions.update({hs_code: RVC_0 for hs_code in hs_map.get_hs_codes(ch_1, ch_2)})
            else:
                exemptions.update({hs_code: RVC_0 for hs_code in hs_map.get_hs_codes(hs_code1, hs_code2)})

        # Inside the group, but self
        group_exempt = regex.compile(r'any other {0} within that group'.format(HS_TIER))
        if group_exempt.search(clause):
            # Assumption, {0} always subheading
            unique_levels = set([hs_code[:6] for hs_code in hs_codes])
            for unique_hs in unique_levels:
                exemptions.update({hs_code: RVC_0 for hs_code in hs_map.get_hs_codes(unique_hs)})

        ## IGNORE THIS CASE FOR A WHILE
        # # Rare case, example: "from any subheading outside that group within heading 29.21"
        # anti_exempt = regex.compile(r'any subheading outside that group')
        # if anti_exempt.search(clause):
        #     exemptions -= Pattern.get_restrictions(hs_codes, 6, hs_map)

        return exemptions
