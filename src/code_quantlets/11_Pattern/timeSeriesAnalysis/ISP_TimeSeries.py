""" Time Series Analysis of  global CO2-levels """

# author: thomas haslwantere; date: Dec-2021

# Standard modules
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import os

# modules from 'statsmodels'
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels import tsa

# additional packages
import matplotlib as mpl

# Set a few style options ---------------------
import sys
sys.path.append(os.path.join('..', 'Utilities'))

try:
# Import formatting commands if directory "Utilities" is available
    from ISP_mystyle import setFonts, showData

except ImportError:
# Ensure correct performance otherwise
    def setFonts(*options):
        return
    def showData(*options):
        plt.show()
        return
# -----------------------------------------------


def get_CO2_data() -> pd.DataFrame:
    """Read in data, and return them as a pandas DataFrame

    Returns
    -------
    df : time stamped recordings of CO2-levels at Mauna Loa, Hawaii
    """

    # Get the data, display a few values, and show the data
    url = 'https://www.esrl.noaa.gov/gmd/webdata/ccgg/trends/co2/co2_mm_mlo.txt'
    df = pd.read_csv(url,
                     skiprows=53,
                     delim_whitespace=True,
                     names = ['year', 'month', 'time', 'co2', 'deseasoned',
                               'nr_days', 'std_days', 'uncertainty'])

    # Display the top values, and show CO2-levels as a function of time
    print(df.head())
    df.plot('time', 'co2')
    plt.show()

    return df


def acf_and_pacf(df: pd.DataFrame) -> None:
    """ Make a seasonal decomposition of the input data, and show the
    autocorrelation (ACF) and partial autocorrelation (PACF) of the residuals.

    Parameters
    ----------
    df : time stamped recordings of CO2-levels at Mauna Loa, Hawaii
    """
    # Seasonal decomposition
    result_add = seasonal_decompose(df['co2'], model='additive', period=12,
            extrapolate_trend='freq')
    result_add.plot()

    out_file = 'TSA_decomposition.jpg'
    showData(out_file)

    plt.plot(result_add.resid, '-')
    # plt.xlim(0, 100)

    # Autocorrelation function ...
    plot_acf(result_add.resid)
    out_file = 'TSA_acf.jpg'
    showData(out_file)

    # ... and partial acf
    plot_pacf(result_add.resid)
    out_file = 'TSA_pacf.jpg'
    showData(out_file)

    return result_add


def fit_ARIMA_models(seasonal_decomposition: pd.DataFrame) -> None:
    """ Take the output from the statsmodels seasonal decomposition, and fit
    different ARIMA models to these data.

    Parameters
    ----------
    seasonal_decomposition : Trend, Seasonal, and Residuals from the CO2-data
    """

    # ARIMA models of the data, to interpret the remaining residuals
    # Fit two different ARIMA-models:
    orders = [(1, 0, 1),
              (0, 0, 2)]

    for order in orders:
        model = ARIMA(seasonal_decomposition.resid, order=(1,0,1))
        model_fit = model.fit()
        print(model_fit.summary())

    # Generate a clear ARIMA model, ...
    # ... plot it, ...
    print('Generate a clear ARIMA model, plot it')
    x = [0, 0]
    for ii in range(200):
        x.append(x[-1] - 0.5*x[-2] + float(np.random.randn(1)))

    plt.plot(x)
    plt.show()

    plot_acf(np.array(x))
    plt.show()

    # ... and fit it
    model = ARIMA(np.array(x), order=(2,0,0))
    model_fit = model.fit()
    print(model_fit.summary())

    print('And now with "statsmodels":')
    # Generate and fit two ARIMA-models with 'statsmodels'
    np.random.seed(12345)
    arparams = np.array([.75, -.25])
    maparams = np.array([.65, .35])
    ar = np.r_[1, -arparams] # add zero-lag and negate
    ma = np.r_[1, maparams] # add zero-lag
    arma_process = tsa.arima_process.ArmaProcess(ar, ma)
    y = arma_process.generate_sample(250)

    model = tsa.arima.model.ARIMA(y, order=(2, 0, 2), trend='n')
    fit = model.fit()
    print(fit.summary())


if __name__ == '__main__':
    data = get_CO2_data()
    decomposed = acf_and_pacf(data)
    fit_ARIMA_models(decomposed)
