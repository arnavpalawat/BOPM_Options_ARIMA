import datetime

import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA


def test_type(data):
    plot_acf(data, lags=40)
    plot_pacf(data, lags=40)
    plt.show()


def fetch_data(ticker, start_date, end_date):
    """Fetch historical data for a given ticker."""
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        print("Fetched data head:", data.head())
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def preprocess_data(data):
    """Preprocess data by dropping unnecessary columns and NaNs."""
    columns_to_drop = ["Open", "High", "Low", "Adj Close", "Volume"]
    data = data.drop(columns=columns_to_drop)
    data = data.dropna()
    print("Data columns after preprocessing:", data.columns)
    return data


def plot_close_prices(data):
    """Plot the closing prices."""
    data["Close"].plot(figsize=(12, 5))
    plt.title('Close Prices')
    plt.grid(True)
    plt.show()


def plot_rolling_statistics(data):
    """Plot rolling mean and standard deviation of the closing prices."""
    mean = data["Close"].rolling(window=12).mean()
    std = data["Close"].rolling(window=12).std()

    plt.plot(mean, color='red', label='Rolling Mean')
    plt.plot(std, color='green', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean and Std')
    plt.grid(True)
    plt.show()


def plot_log_transformation(data):
    """Apply log transformation and plot the log-scaled closing prices."""
    log_scale = np.log(data['Close'])
    moving_average = log_scale.rolling(window=12).mean()
    moving_std = log_scale.rolling(window=12).std()

    plt.plot(log_scale, label='Log Scale')
    plt.plot(moving_average, color='red', label='Moving Average')
    plt.legend(loc='best')
    plt.title('Log Transformation with Moving Average')
    plt.grid(True)
    plt.show()

    return log_scale, moving_average


def plot_transformed_data(log_scale, moving_average):
    """Transform the time series and plot."""
    log_transformed = log_scale - moving_average
    log_transformed.dropna(inplace=True)

    plt.figure(figsize=[10, 6])
    moving_average = log_transformed.rolling(window=12).mean()
    moving_std = log_transformed.rolling(window=12).std()

    plt.plot(log_transformed, color='blue', label='Original')
    plt.plot(moving_average, color='red', label='Rolling Mean')
    plt.plot(moving_std, color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Transformed Data with Rolling Mean & Std')
    plt.grid(True)
    plt.show()


def plot_time_shift(log_scale):
    """Plot time-shifted log-scaled data."""
    shifting = log_scale - log_scale.shift()

    plt.figure(figsize=[10, 6])
    plt.plot(shifting, color='m')
    plt.title('Time Shifted Log Scale')
    plt.grid(True)
    plt.show()


def ad_test(dataset):
    """Perform ADF test and print results."""
    dftest = adfuller(dataset, autolag='AIC')
    print("1. ADF Statistic : ", dftest[0])
    print("2. P-Value : ", dftest[1])
    print("3. Number of Lags : ", dftest[2])
    print("4. Number of Observations Used For ADF Regression:", dftest[3])
    print("5. Critical Values :")
    for key, val in dftest[4].items():
        print(f"\t {key}: {val}")


def arima(data, future_periods=30):
    # Ensure the index has a frequency set
    data.index = pd.to_datetime(data.index)
    data = data.asfreq('D')  # Set frequency to daily

    # Fit the ARIMA model on the full dataset
    model = ARIMA(data['Close'], order=(0, 1, 1))
    model_fit = model.fit()

    # Print model summary
    print(model_fit.summary())

    # Forecast future periods
    forecast_results = model_fit.get_forecast(steps=future_periods)
    forecast_means = forecast_results.predicted_mean
    print("Forecast means head:", forecast_means.head())

    # Create a date range for future predictions
    future_dates = pd.date_range(start=data.index[-1], periods=future_periods + 1)[1:]

    # Create a Series with forecasted values
    future_forecast_series = pd.Series(forecast_means, index=future_dates)

    # Create a plot to compare the forecast with the actual data
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Historical Data')
    plt.plot(future_forecast_series, label='Forecasted Data', color='green')
    plt.fill_between(future_dates,
                     forecast_results.conf_int().iloc[:, 0],
                     forecast_results.conf_int().iloc[:, 1],
                     color='k', alpha=.15)
    plt.title('ARIMA Model Future Prediction')
    plt.xlabel('Date')
    plt.ylabel('Close')
    plt.legend()
    plt.show()

    return future_forecast_series


def analyze_ticker(ticker, start_date=str(datetime.datetime.today() - datetime.timedelta(days=1095)).split()[0], end_date=str(datetime.datetime.today()).split()[0]):
    """Main logic to analyze a specific ticker."""
    # Fetch and preprocess data
    data = fetch_data(ticker, start_date, end_date)
    if data is not None:
        data = preprocess_data(data)

        # Plot data and statistics
        plot_close_prices(data)
        plot_rolling_statistics(data)
        log_scale, moving_average = plot_log_transformation(data)
        plot_transformed_data(log_scale, moving_average)
        plot_time_shift(log_scale)
        log_transformed = log_scale - moving_average
        log_transformed.dropna(inplace=True)

        # Perform ADF test
        ad_test(log_transformed)

        # Perform ARIMA and get future predictions
        dataset = log_transformed.to_frame()
        future_predictions = arima(dataset, future_periods=365)

        # Define x as the indices of the series
        x = np.arange(len(future_predictions))

        # Perform linear regression to find m and b
        m, b = np.polyfit(x, future_predictions, 1)

        print("LOG EQUATION: ", "y =", m, "x +", b)
        return m * 365 + b
