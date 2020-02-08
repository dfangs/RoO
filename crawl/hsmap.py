"""
hsmap.py
Author: Dean Fanggohans
Last update: 12:20 EST, November 24, 2019
"""

import pandas as pd

## -----------------------------------------------------------------------------
## Class Definition
## -----------------------------------------------------------------------------

class HSMap:
    """Represent a version of Harmonized System (HS) Product Nomenclature table
    (up to six-digit level).

    Methods:
      get_hs_codes():
        Return a list of all HS codes under given (possibly range of) two- to six-digit HS code(s).
    """
    def __init__(self, version, filename):
        """Initialize an instance of HSMap.

        Inputs:
          `version`: string or an integer representing the version of the HS Nomenclature used
          `filename`: string of file directory containing the .csv file of the HS Nomenclature
        """
        self.version = version
        df = pd.read_csv(filename)
        # self.database = df.loc[df['Tier'] == 3, 'ProductCode'].tolist()
        self.database = df.loc[(df['isLeaf'] == 1) & ~(df['Code'].str.startswith('99')), 'Code'].tolist()
        self.full_map = self.expand_map()

    def __len__(self):
        return len(self.database)

    # CREATE A DICTIONARY FOR FASTER ACCESS TO ALL HS CODES
    def expand_map(self):
        """Given two- to six-digit of HS code (chapter, heading, or subheading),
        return a list containing all 6-digit HS codes within it.

        Side note: Could have implemented this as a recursive data structure,
                   but would be slower.
                   Just want the benefit of hash table (dict) fast look-up.

        This implementation assumes given database (which comes from .csv file)
        is already sorted.
        """
        full_map = {}
        for hs_code in self.database:
            full_map.setdefault(hs_code[:2], []).append(hs_code)
            full_map.setdefault(hs_code[:4], []).append(hs_code)
            full_map.setdefault(hs_code, []).append(hs_code)
        return full_map

    # FUNCTION FOR EXTRACTING HS CODES
    def get_hs_codes(self, hs_code1, hs_code2=''):
        """Given a range of (or even single) HS codes, return a list of all HS codes in-between.

        Inputs:
          `hs_code1`, `hs_code2`: strings representing HS code

        Output:
          A list of all HS codes between `hs_code1` and `hs_code2` (inclusive), or just all HS codes
          contained within `hs_code1` if `hs_code2` is not given.
        """
        # Clean HS codes
        hs_code1 = hs_code1.replace('.', '')
        hs_code2 = hs_code2.replace('.', '')

        if not hs_code2:
            try:
                return self.full_map[hs_code1]
            except KeyError:
                print("HS code not found!")
                print('Previous search: ' + hs_code1, end='\n\n')
                raise KeyError
        else:
            try:
                index_1 = self.database.index(self.full_map[hs_code1][0])
                index_2 = self.database.index(self.full_map[hs_code2][-1])
            except KeyError:
                print("HS code not found!")
                print('Previous search: ' + hs_code1 + '-' + hs_code2, end='\n\n')
                raise KeyError
            else:
                return self.database[index_1:index_2+1]

    def get_all_hs_codes(self):
        """Return a list of all HS codes."""
        return self.database[:]
