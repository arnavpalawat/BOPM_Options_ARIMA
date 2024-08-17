from state_prediction import analyze_ticker
import yfinance as yf


def main():
    # Get ticker
    ticker = input("Enter the ticker symbol to analyze: ")
    ticker_data = yf.Ticker(ticker)

    # Get states
    middle_state = analyze_ticker(ticker)
    s_sub_u_percent = middle_state + 0.02
    s_sub_d_percent = middle_state - 0.02
    hist = ticker_data.history(period="1d")
    close_price = hist['Close'].iloc[-1]

    # States
    s_sub_u = s_sub_u_percent * close_price
    s_sub_d = s_sub_d_percent * close_price


if __name__ == "__main__":
    main()
