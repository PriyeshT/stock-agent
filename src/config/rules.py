# DO NOT MODIFY without explicit confirmation from Priyesh.
# These are the buy/sell rules the portfolio agent enforces every week.

BUY_RULES: dict = {
    "signal_required": "GREEN",           # Only buy when weekly signal is GREEN
    "max_positions": 3,                    # Never hold more than 3 stocks at once
    "buy_frequency": "last_monday_of_month",
    "no_buy_within_days_of_event": 7,      # No buying 7 days before earnings/dividends
    "no_averaging_down": True,             # Never buy more of a losing position
}

SELL_RULES: dict = {
    "partial_exit_at_gain_pct": 25,        # Sell half the position at +25%
    "full_exit_at_gain_pct": 50,           # Sell the rest at +50%
    "hard_stop_loss_pct": -15,             # Exit everything at -15% loss
    "story_change": True,                  # Sell if the investment thesis breaks
    "yellow_weeks_before_exit": 3,         # Exit after 3 consecutive YELLOW weeks
}

# The three states a position can be in
POSITION_STATES: list[str] = ["ACTIVE", "PARTIAL", "CLOSED"]

# The three signal states the research agent can return for any stock
SIGNAL_STATES: list[str] = ["GREEN", "YELLOW", "RED"]
