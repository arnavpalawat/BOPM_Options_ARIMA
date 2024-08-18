import yfinance as yf


def calculate_intrinsic_values(s_sub_u, s_sub_d, strike, option_type):
    if option_type == "calls":
        s_sub_u_iv = max(s_sub_u - strike, 0)
        s_sub_d_iv = 0
    else:  # option_type == "puts"
        s_sub_u_iv = 0
        s_sub_d_iv = max(strike - s_sub_d, 0)
    return s_sub_u_iv, s_sub_d_iv


def calculate_delta(s_sub_u, s_sub_d, s_sub_u_iv, s_sub_d_iv, option_type):
    if s_sub_u == s_sub_d:
        raise ValueError("s_sub_u and s_sub_d cannot be equal, as it would result in division by zero.")

    if option_type == "calls":
        DELTA = (s_sub_d_iv - s_sub_u_iv) / (s_sub_d - s_sub_u)
    else:  # option_type == "puts"
        DELTA = (s_sub_u_iv - s_sub_d_iv) / (s_sub_d - s_sub_u)

    return DELTA


def calculate_option_value(s_sub_u_iv, s_sub_d_iv, DELTA, s_sub_u, close_price, middle_state):
    P_sub_c = -s_sub_u_iv + DELTA * s_sub_u
    print(f"P_sub_c: {P_sub_c}")

    try:
        treasury_yield10 = yf.Ticker("^TNX")
        risk_free_rate = round(treasury_yield10.info['regularMarketPreviousClose'] / 100, 2)
    except KeyError:
        raise RuntimeError("Could not retrieve risk-free rate from Yahoo Finance.")
    except Exception as e:
        raise RuntimeError(f"An error occurred while retrieving risk-free rate: {e}")

    # PV of P_sub_c (Assume WACC = RFR, T = 1 year)
    P = P_sub_c / (1 + risk_free_rate)
    V = DELTA * (close_price * (1 + middle_state)) - P
    return V


def perform_calculations(s_sub_u, s_sub_d, strike, close_price, middle_state):
    # Get Option Type
    type_int = 0
    option_type = "puts" if type_int == 1 else "calls"

    # Get Intrinsic Values
    s_sub_u_iv, s_sub_d_iv = calculate_intrinsic_values(s_sub_u, s_sub_d, strike, option_type)

    print(f"Strike Price: {strike}")
    print(f"s_sub_u: {s_sub_u}")
    print(f"s_sub_d: {s_sub_d}")
    print(f"Intrinsic Value (up state): {s_sub_u_iv}")
    print(f"Intrinsic Value (down state): {s_sub_d_iv}")

    # Calculate Delta
    try:
        DELTA = calculate_delta(s_sub_u, s_sub_d, s_sub_u_iv, s_sub_d_iv, option_type)
        print(f"Delta: {DELTA}")
    except ValueError as e:
        print(f"Error calculating Delta: {e}")
        return

    # Calculate Option Value
    V = calculate_option_value(s_sub_u_iv, s_sub_d_iv, DELTA, s_sub_u, close_price, middle_state)
    print(f"Option Value: {V}")

