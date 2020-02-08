"""
In this file, you only need to type the import statements below.
Nevertheless, these actual modules need (at least) `regex` and `pandas` to run.

Easiest way to install all dependencies (and also the one that I use):
1) Install Anaconda (note: the size it quite big)
   Link: https://www.anaconda.com/distribution/#download-section
2) Open Anaconda Prompt
3) Type 'pip install regex' on the terminal to install regex
   (If this doesn't work, there is another way to install regex
    via Anaconda Navigator.)

Alternative way:
Use Google Colab (work on progress).
"""

import matplotlib.pyplot as plt
from roo import RoO
from hsmap import HSMap

if __name__ == "__main__":
    # Read csv files of different versions of HS code mapping
    hs_maps = {
        1992: HSMap('1992', '../hs_maps/H0.csv'),
        1996: HSMap('1996', '../hs_maps/H1.csv'),
        2002: HSMap('2002', '../hs_maps/H2.csv'),
        2007: HSMap('2007', '../hs_maps/H3.csv'),
        2012: HSMap('2012', '../hs_maps/H4.csv'),
        2017: HSMap('2017', '../hs_maps/H5.csv')
    }

    with open('../clean_pta/NAFTA.txt', mode='r', encoding='utf-8') as f:
        nafta = f.read()

    NAFTA = RoO('NAFTA', nafta, hs_maps[1992])

    # Print summary of the FTA
    NAFTA.summarize(only=3)

    # Alter figure size
    # plt.figure(figsize=(15.5,7.75))
    # NAFTA.plot_chapter_restrictions()

    plt.figure(figsize=(15.5,7.75))
    NAFTA.scatter_plot()

    # Uncomment if want to look at the plot
    # plt.show()

    # Uncomment this if you want direct access to the pandas DataFrame
    # nafta_df = NAFTA.restrictions_table(VA=True)

    # Generate dataset
    # Instead of dta, you can also use csv or xlsx; just specify it in the function
    # Note: generating xlsx file is much slower in my computer
    # NAFTA.generate_dataset('csv', VA=True)
