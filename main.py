import yfinance as yf
from hedging_calculation import perform_calculations
from state_prediction import analyze_ticker


def main():
    try:
        # Get ticker
        ticker = input("Enter the ticker symbol to analyze: ").strip()
        if not ticker:
            raise ValueError("Ticker symbol cannot be empty.")

        ticker_data = yf.Ticker(ticker)
        hist = ticker_data.history(period="1d")
        if hist.empty:
            raise ValueError(f"No data found for ticker symbol: {ticker}")

        # Get states
        try:
            middle_state = analyze_ticker(ticker)
        except Exception as e:
            raise RuntimeError(f"Error analyzing ticker: {e}")

        # Get T + 1 States
        s_sub_u_percent = middle_state + 0.01
        s_sub_d_percent = middle_state - 0.01
        close_price = hist['Close'].iloc[-1]
        print("Current Price:", close_price)

        # States @ T + 1
        s_sub_u = close_price * (1 + s_sub_u_percent)
        s_sub_d = close_price * (1 + s_sub_d_percent)

        # Get Strike Price
        try:
            strike = float(input("Enter the desired strike price: ").strip())
        except ValueError:
            raise ValueError("Invalid strike price. Please enter a valid number.")

        # Perform calculations
        try:
            perform_calculations(s_sub_u, s_sub_d, strike, close_price, middle_state)
        except Exception as e:
            raise RuntimeError(f"Error performing calculations: {e}")

    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
