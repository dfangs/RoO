"""
roo.py
Author: Dean Fanggohans
Last modified: 18:30 EST, January 19, 2020
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import regex

from collections import Counter
from pattern import Pattern, raw_patterns, categories, HSC_RANGE_8, HSC_GROUP_8, HSC_GROUP_8_NC
import pprint

## -----------------------------------------------------------------------------
## Globals
## -----------------------------------------------------------------------------

search_patterns = {}
for name, category in categories.items():
    search_patterns[name] = Pattern(name, raw_patterns[name], category)

## -----------------------------------------------------------------------------
## Class Definition
## -----------------------------------------------------------------------------

class RoO:
    """Represent the Rules of Origin (with relevant methods) of a single FTA.

    Methods:
      plot_chapter_restrictions():
        Create a line plot of cumulative roo_1 (y-axis) vs HS chapter (x-axis).
      scatter_plot():
        Create a scatter plot of roo_1 (y-axis) vs HS chapter (x-axis).
      restrictions_table():
        Return a list of all HS codes under given (possibly range of) two- to six-digit HS code(s).
      get_restrictions():
        Return a list of all restricted outputs given a certain input.
      summarize():
        Print a summary of the FTA (including statistics and debugging functionality).
    """
    def __init__(self, name, raw_text, hs_map, structured=False, patterns=search_patterns):
        """Initialize an instance of RoO.

        Inputs:
          `name`: string representing the name of FTA
          `raw_text`: string of the whole content of rules of origin (starting from
                      'Product Specific Rules' section)
          `hs_map`: instance of HSMap used throughout the rules
          `structured`:
          `pattern_types`: dict of reference used to classify and process rules of origin
        """
        self.name = name
        self.hs_map = hs_map
        if structured:
            self.structure = self.parse_structure(raw_text)
            self.unique_rules, self.all_rules = self.expand_rules()
        else:
            self.unique_rules, self.all_rules = self.parse_rules(raw_text)
            # self.structure = self.build_structure()
        self.va_requirements = {hs_code: [0, 0] for hs_code in self.all_rules}
        self.restrictions = self.build_restrictions(patterns)

    def __len__(self):
        return len(self.all_rules)

    def parse_structure(self, raw_text):
        """Given a complete text of Specific Rules of Origin, return a dictionary representing
        the complete hierarchical structure of RoO (from sections to chapters).

        Inputs:
          `raw_text`: string containing the entire text of RoO
        """
        # Clean whitespaces; replace en dash with hyphen
        # Code below assumes no multiple adjacent whitespaces; see previous code to rollback
        roo_text = regex.sub(r'\s?[–\-]\s?', '-', regex.sub(r'\s+', ' ', raw_text))

        # Capture sections
        pattern_section = regex.compile(r'(?i)(Section [IVX]{1,5})[\s\-](.+?)(?=Section [IVX]{1,5}[\s\-][A-Z]|\Z)', flags=regex.DOTALL)
        result = pattern_section.findall(roo_text)
        structure = {match[0]: match[1] for match in result}

        # Capture chapters in every section
        pattern_chapter = regex.compile(r'(Chapter \d{1,2})[\s\-](.+?)(?=Chapter \d{1,2}[\s\-][A-Z]|\Z)', flags=regex.DOTALL)
        for section, content in structure.items():
            result = pattern_chapter.findall(content)
            structure[section] = {match[0]: match[1] for match in result}

        # Capture rules in every chapter
        pattern_rule = regex.compile(r'{0}\s+([A-Z].+?\.)(?=\s+{1}|\s*\Z)'.format(HSC_GROUP_8, HSC_GROUP_8_NC), flags=regex.DOTALL)
        for section in structure:
            for chapter, rules in structure[section].items():
                result = pattern_rule.findall(rules)
                structure[section][chapter] = {match[0]: match[3] for match in result}

        return structure

    def expand_rules(self):
        """Return a dictionary mapping (range of) HS codes to a rule of origin, both
        represented as strings; essentially storing the rules without stuctures.
        """
        unique_rules, all_rules = {}, {}
        # UPDATE: WILL NOT ALLOW TARIFF ITEM RULES -> instead of directly compiling HS_RANGE, use a modified version
        pattern_range = regex.compile(HSC_GROUP_8)
        for section in self.structure:
            for chapter in self.structure[section]:
                for hs_code_range, rule in self.structure[section][chapter].items():
                    # Ignore tariff item
                    if len(hs_code_range.split('-')[0].replace('.', '')) > 6:
                        continue
                    unique_rules[hs_code_range] = rule

                    # I use findall instead of search since it returns '' instead of None
                    result = pattern_range.findall(hs_code_range)
                    hs_codes = self.hs_map.get_hs_codes(result[0][1], result[0][2])
                    for hs_code in hs_codes:
                        all_rules[hs_code] = rule

        return unique_rules, all_rules

    def parse_rules(self, raw_text):
        """Given a complete text of Specific Rules of Origin, return a dictionary
        mapping (range of) HS codes to a rule of origin, both represented as strings.

        Sort of like parse_roo() combined with expand_rules(), but without having to
        rely on RoO hierarchical structure.

        Inputs:
          `raw_text`: string containing the entire text of RoO
        """
        # Clean whitespaces; replace en dash with hyphen
        # Code below assumes no multiple adjacent whitespaces; see previous code to rollback
        roo_text = regex.sub(r'\s?[–\-]\s?', '-', regex.sub(r'\s+', ' ', raw_text))
        unique_rules, all_rules = {}, {}

        # Capture all rules simultanously
        pattern_rule_v2 = regex.compile(r'((?:A|No|No required) change (?:[\w\W](?!provided))+? {0}[\w\W]+?(?:[^\.\s]\w|\s\d)\.(?=\s+[A-Z0-9]|\s*\Z))'.format(HSC_RANGE_8))
        for match in pattern_rule_v2.findall(roo_text):
            hs_code1 = match[1].replace('.', '')
            hs_code2 = match[2].replace('.', '')

            # Ignore tariff item
            if len(hs_code1) > 6 or len(hs_code2) > 6:
                continue

            hs_code_range = hs_code1 + '-' + hs_code2 if hs_code2 else hs_code1
            unique_rules.setdefault(hs_code_range, []).append(match[0])

            hs_codes = self.hs_map.get_hs_codes(hs_code1, hs_code2)
            for hs_code in hs_codes:
                all_rules.setdefault(hs_code, []).append(match[0])

        return {k: ' '.join(v) for k, v in unique_rules.items()}, {k: ' '.join(v) for k, v in all_rules.items()}

    def build_restrictions(self, patterns):
        """Return a dictionary mapping each (output) HS code to a list of tuples
        (hs_code, restrictiveness), where:
          `hs_code`: string of HS code representing input product
          `restrictiveness`: float (0, 1] representing CTC (value of 1) or
                             VA requirement percentage (value of less than 1)

        Side note: Order of output-input can be exchanged, or even better, use
                   numpy array then transpose.
        """
        restrictions = {}
        pattern_range = regex.compile(HSC_GROUP_8)
        for hs_code_range, rule in self.unique_rules.items():
            # Get HS codes
            result = pattern_range.findall(hs_code_range)
            hs_codes = self.hs_map.get_hs_codes(result[0][1], result[0][2])

            # Classify the rules
            for name, pattern in patterns.items():
                result = pattern.search(hs_codes, rule, self.hs_map)
                if result:
                    for hs_final in hs_codes:
                        # Added code below to classify va_c or va_a
                        self.classify_va(hs_final, name)
                        all_restrictions = pattern.finalize(hs_final, result, self.hs_map)
                        for hs_intermediate, restrictiveness in all_restrictions.items():
                            restrictions.setdefault(hs_intermediate, {}).update({hs_final: restrictiveness})
                    # Assuming a rule only belongs to one type
                    break

        return restrictions

    def plot_chapter_restrictions(self):
        """Make a line plot of cumulative roo1 (y-axis) vs HS chapter (x-axis)."""
        freq = Counter()
        for hs_code, restrictions in self.restrictions.items():
            for restrictiveness in restrictions.values():
                if restrictiveness == 0:
                    continue
                freq[hs_code[:2]] += 1

        restrictions_by_chapter = [0 for i in range(98)]
        for key, value in freq.items():
            restrictions_by_chapter[int(key)] = value

        plt.plot(restrictions_by_chapter, label=self.name)
        plt.xlabel('HS Chapter')
        plt.ylabel('Total Restrictiveness Index')

    def scatter_plot(self):
        """Make a scatter plot of roo_1 (y-axis) vs HS chapter (x-axis)."""
        chapters = []
        restrictiveness_index = []
        for hs_code, restrictions in self.restrictions.items():
            count = 0
            for restrictiveness in restrictions.values():
                if restrictiveness == 0:
                    continue
                count += 1
            chapters.append(int(hs_code[:2])/10)
            restrictiveness_index.append(count)

        plt.scatter(chapters, restrictiveness_index, label=self.name)
        plt.xlabel('HS Chapter (first digit)')
        plt.ylabel('Restrictiveness Index')

    def restrictions_table(self, VA=False):
        """Return a DataFrame representing the final data set."""
        data = {'VAAR_dummy': [], 'output_str': [], 'input_str': [], 'VA_Percentage': []}
        if VA:
            data.update({'VA_Complement': [], 'VA_Alternative': []})
        for hs_intermediate, restrictions in self.restrictions.items():
            for hs_final, restrictiveness in restrictions.items():
                if restrictiveness == 0:
                    continue
                data['VAAR_dummy'].append(1)
                data['output_str'].append(hs_final)
                data['input_str'].append(hs_intermediate)
                data['VA_Percentage'].append(restrictiveness)
                if VA:
                    data['VA_Complement'].append(self.va_requirements[hs_final][0])
                    data['VA_Alternative'].append(self.va_requirements[hs_final][1])
        return pd.DataFrame.from_dict(data)

    def classify_va(self, hs_code, pattern_name):
        """Helper function to classify whether there is a complement VA requirement
        or alternative VA requirement within a rule.
        """
        # Complementary
        if pattern_name.endswith('+RVC') and '_or_' not in pattern_name:
            self.va_requirements[hs_code][0] = 1
        # Alternative
        if '_or_' in pattern_name:
            self.va_requirements[hs_code][1] = 1

    def get_restrictions(self, hs_intermediate):
        """Return a list of restricted HS codes of final product (output) given
        the HS code of intermediate product (input).

        Input:
          `hs_intermediate`: string of HS code, representing an input product
        """
        if hs_intermediate in self.restrictions:
            return sorted([hs_final for hs_final in self.restrictions[hs_intermediate]])
        else:
            print('This HS Code does not have any rules imposed.')

    def summarize(self, type_='', patterns=search_patterns, only=None,
                  remaining=False, duplicates=True, unaffected=False,
                  countRules=False, simple=False):
        """Print a summary of the FTA, which could include statistics of each type of rules,
        total coverage of RoO, number of remaining rules, etc.

        Can also be used as a tool for debugging (i.e. detecting duplicate rules, uncaptured
        rules, or even looking for specific type of rules).
        """
        uncaptured = 0
        freqHS, freqRules = Counter(), Counter()
        pattern_range = regex.compile(HSC_GROUP_8)
        for hs_code_range, rule in self.unique_rules.items():
            types = []
            for name, pattern in patterns.items():
                if pattern.check(rule):
                    types.append(name)
                    if name == type_:
                        print(rule, end='\n\n')
            if len(types) == 0:
                uncaptured += 1
                if remaining:
                    print(rule, end='\n\n')
            elif len(types) > 1:
                if duplicates:
                    print(types)
                    print(rule, end='\n\n')
            else:
                result = pattern_range.findall(hs_code_range)
                freqHS[types[0]] += len(self.hs_map.get_hs_codes(result[0][1], result[0][2]))
                freqRules[types[0]] += 1

        if unaffected:
            print('HS codes without any rules:')
            print(sorted(set(self.hs_map.get_all_hs_codes()) - set(self.all_rules)), end='\n\n')

        covered, total = sum(freqHS.values()), len(self.all_rules)

        if simple:
            print('{}\t  {} / {}   ({:2.2%}) [{}]'.format(self.name, str(covered).rjust(4), str(total).rjust(4),
                                                          covered/total, len(self.hs_map)))
        else:
            print(self.name)
            print('Rules left:', uncaptured, '/', len(self.unique_rules))
            print('Counter: ', end='')
            if countRules:
                pprint.pprint(freqRules.most_common(only))
            else:
                pprint.pprint(freqHS.most_common(only))
            print(covered, '/', total, '({:2.2%})'.format(covered / total))
            print('HSMap size:', len(self.hs_map), end='\n\n')

    def generate_report(self, patterns=search_patterns):
        """Generate a summary of the FTA, which could include statistics of each type of rules,
        total coverage of RoO, number of remaining rules, etc.

        Output: dictionary mapping ...
        """
        uncaptured = 0
        freqHS, freqRules = Counter(), Counter()
        pattern_range = regex.compile(HSC_GROUP_8)
        for hs_code_range, rule in self.unique_rules.items():
            types = []
            for name, pattern in patterns.items():
                if pattern.check(rule):
                    types.append(name)
            if len(types) == 0:
                uncaptured += 1
            elif len(types) > 1:
                print('There is a duplicate! Refine pattern.py first.')
                raise ValueError
            else:
                result = pattern_range.findall(hs_code_range)
                freqHS[types[0]] += len(self.hs_map.get_hs_codes(result[0][1], result[0][2]))
                freqRules[types[0]] += 1

        report = {
            'uncaptured': uncaptured,
            'totalRules': len(self.unique_rules),
            'totalHS': len(self.all_rules),
            'HSMap_ver': self.hs_map.version,
            'HSMap_len': len(self.hs_map)
        }
        report.update({name: (count, freqRules[name]) for name, count in freqHS.items()})

        return report

    def generate_dataset(self, filetype, filepath=None, VA=False):
        """Generate dataset with the specified file type.
        Available options: csv, dta, xlsx
        """
        df = self.restrictions_table(VA).sort_values(by=['output_str', 'input_str']).reset_index(drop=True)
        if filepath is None:
            filepath = self.name + '.' + filetype

        if filetype == 'csv':
            df.to_csv(path_or_buf=filepath, index=False)
        elif filetype == 'dta':
            df.to_stata(fname=filepath, write_index=False)
        elif filetype == 'xlsx':
            df.to_excel(excel_writer=filepath, index=False)
        else:
            print('Filetype not recognized!')
            raise ValueError
