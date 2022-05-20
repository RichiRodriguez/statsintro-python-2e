"""Analysis of one group of data

This script shows how to
- Use a t-test for a single mean
- Use a non-parametric test (Wilcoxon signed rank sum) to check a single mean
- Compare the values from t-distribution with those of a normal distribution
"""

# author: Thomas Haslwanter, date: Dec-2021


# Import standard packages
import numpy as np
import scipy.stats as stats
import pingouin as pg
from pprint import pprint


def check_mean() -> float:
    """Data from Altman, check for significance of mean value.
    Compare average daily energy intake (kJ) over 10 days of 11 healthy women,
    and compare it to the recommended level of 7725 kJ.

    Returns
    -------
    p-value : just for testing the function
    """

    # Get data from Altman
    inFile = 'altman_91.txt'
    data = np.genfromtxt(inFile, delimiter=',')

    # Watch out: by default the standard deviation in numpy is calculated with
    # ddof=0, corresponding to 1/N!
    myMean = np.mean(data)
    mySD = np.std(data, ddof=1)     # sample standard deviation
    print(('Mean and SD: {0:4.2f} and {1:4.2f}'.format(myMean, mySD)))

    # Confidence intervals
    tf = stats.t(len(data)-1)
    # multiplication with np.array[-1,1] is a neat trick to implement "+/-"
    ci = np.mean(data) + stats.sem(data)*np.array([-1,1])*tf.ppf(0.975)
    print(('The confidence intervals are {0:4.2f} to {1:4.2f}.'.format(ci[0], ci[1])))

    # Check if there is a significant difference relative to "checkValue"
    checkValue = 7725
    # --- >>> START stats <<< ---
    t, prob = stats.ttest_1samp(data, checkValue)
    if prob < 0.05:
        print(f'{checkValue:4.2f} is significantly different '+
              f'from the mean (p={prob:5.3f}).')

    # For not normally distributed data, use the Wilcoxon signed rank sum test
    (rank, pVal) = stats.wilcoxon(data-checkValue)
    if pVal < 0.05:
      issignificant = 'unlikely'
    else:
      issignificant = 'likely'
    # --- >>> STOP stats <<< ---

    print(f'It is {issignificant} that the value is {checkValue:d}')

    return prob # should be 0.018137235176105802


def explain_power() -> None:
    """ Reproduce most of the parameters from pingouin's 'ttest' """

    # generate the data
    np.random.seed(12345)
    n = 100
    data = stats.norm(7,3).rvs(n)

    # analysis parameters
    c = 6.5
    alpha = 0.05

    # standard parameters
    mean = np.mean(data)
    sem = stats.sem(data)
    std = np.std(data, ddof=1)
    dof = n-1

    h1 = stats.t(df=len(data)-1, loc=mean, scale=sem)

    # reproduce the results of the pingouin T-test
    results = {}

    results['dof'] = dof
    results['t_val'] = (mean-c)/sem
    results['d'] = (mean-c)/np.std(data, ddof=1)

    tc = stats.t(dof).isf(alpha/2)
    results['p_val'] = stats.t(dof).sf(results['t_val'])*2

    results['ci'] = h1.ppf([alpha/2, 1-alpha/2])

    # power-calculation
    nct = stats.nct(df=dof, nc=(mean-c)/sem)
    results['power'] = nct.sf(tc) + nct.cdf(-tc)

    pprint(results)


def compareWithNormal():
    """ This function is supposed to give you an idea how big/small the
    difference between t- and normal distribution are for realistic
    calculations.
    """

    # generate the data
    np.random.seed(12345)
    normDist = stats.norm(loc=7, scale=3)
    data = normDist.rvs(100)
    checkVal = 6.5

    # T-test
    # --- >>> START stats <<< ---
    t, tProb = stats.ttest_1samp(data, checkVal)
    # --- >>> STOP stats <<< ---

    # Comparison with corresponding normal distribution
    mmean = np.mean(data)
    mstd = np.std(data, ddof=1)
    normProb = stats.norm.cdf(checkVal, loc=mmean,
            scale=mstd/np.sqrt(len(data)))*2

    # compare
    print(f'The probability from the t-test is ' + '{tProb:5.4f}, ' +
          f'and from the normal distribution {normProb:5.4f}')

    return normProb # should be 0.054201154690070759


if __name__ == '__main__':
    check_mean()
    explain_power()
    compareWithNormal()
