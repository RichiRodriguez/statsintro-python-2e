""" Graphical and quantitative check, if a given distribution is normal.
- For small sample-numbers (<50), you should use the Shapiro-Wilk test or
    the "normaltest"
- for intermediate sample numbers, the Lilliefors-test is good since the
   original Kolmogorov-Smirnov-test is unreliable when mean and std of the
   distribution are not known.
- the Kolmogorov-Smirnov(Kolmogorov-Smirnov) test should only be used for large
    sample numbers (>300)
"""

# author: Thomas Haslwanter, date: Dec-2021

# Import standard packages
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd
import pingouin as pg

# additional packages
from statsmodels.stats.diagnostic import lilliefors


def check_normality(show_flag: bool=False):
    """Check if the distribution is normal."""

    # Set the parameters
    numData = 1000
    myMean = 0
    mySD = 3

    # To get reproducable values, I provide a seed value
    np.random.seed(12345)

    # Generate and show random data
    data = stats.norm.rvs(myMean, mySD, size=numData)
    fewData = data[:100]
    if show_flag:
        plt.hist(data)
        plt.show()

    # --- >>> START stats <<< ---
    # Graphical test: if the data lie on a line, they are pretty much
    # normally distributed
    # _ = stats.probplot(data, plot=plt)
    if show_flag:
        pg.qqplot(data)
        plt.show()

    # With pandas Series it is simple to print name/value pairs without any further formatting
    pVals = pd.Series(np.float64)
    pFewVals = pd.Series(np.float64)
    # The scipy normaltest is based on D-Agostino and Pearsons test that
    # combines skew and kurtosis to produce an omnibus test of normality.
    _, pVals['Omnibus']    = stats.normaltest(data)
    _, pFewVals['Omnibus'] = stats.normaltest(fewData)

    # Shapiro-Wilk test
    _, pVals['Shapiro-Wilk']    = stats.shapiro(data)
    _, pFewVals['Shapiro-Wilk'] = stats.shapiro(fewData)

    # Or you can check for normality with Lilliefors-test
    _, pVals['Lilliefors']    = lilliefors(data)
    _, pFewVals['Lilliefors'] = lilliefors(fewData)

    # Alternatively with original Kolmogorov-Smirnov test
    _, pVals['Kolmogorov-Smirnov']    = \
            stats.kstest((data-np.mean(data))/np.std(data,ddof=1), 'norm')
    _, pFewVals['Kolmogorov-Smirnov'] = \
        stats.kstest((fewData-np.mean(fewData))/np.std(fewData,ddof=1), 'norm')

    print(f'p-values for all {len(data)} data points: ----------------')
    print(pVals)
    print('p-values for the first 100 data points: ----------------')
    print(pFewVals)

    if pVals['Omnibus'] > 0.05:
        print('Data are normally distributed')
    # --- >>> STOP stats <<< ---

    return pVals['Kolmogorov-Smirnov']


if __name__ == '__main__':
    p = check_normality()
    print(p)

