#!/usr/bin/env python
# coding: utf-8




from DataLoader import DataLoader
import pandas as pd


class StrategyEngine:
    def __init__(self, data):
        if data is None or data.empty:
            raise ValueError(
                "Input data is empty. Please fetch data before strategy execution."
            )

        self.data = data.copy()

    def _get_close_series(self):

        if "Close" in self.data.columns:
            close = self.data["Close"]
        else:
            close_cols = []

            for col in self.data.columns:
                if "Close" in str(col):
                    close_cols.append(col)

            if len(close_cols) == 0:
                raise KeyError("Close price column not found in input data.")

            close = self.data[close_cols[0]]

        # Convert to Series if needed
        if hasattr(close, "columns"):
            close = close.iloc[:, 0]

        return close.astype(float)

    def calculate_moving_average(self, prices, window):
        moving_averages = []

        for i in range(len(prices)):
            if i < window - 1:
                moving_averages.append(None)
            else:
                total = 0

                for j in range(i - window + 1, i + 1):
                    total += prices.iloc[j]

                average = total / window
                moving_averages.append(average)

        return moving_averages

    def moving_average_crossover(self, short_window=20, long_window=50):
        if short_window <= 0 or long_window <= 0:
            raise ValueError("Window sizes must be positive integers.")

        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window.")

        close = self._get_close_series()

        strategy_df = pd.DataFrame(index=self.data.index)

        strategy_df["Close"] = close

        # Manual moving average calculation
        strategy_df["SMA_Short"] = self.calculate_moving_average(
            close,
            short_window
        )

        strategy_df["SMA_Long"] = self.calculate_moving_average(
            close,
            long_window
        )

        # Position generation
        positions = []
        for i in range(len(strategy_df)):
            short_ma = strategy_df["SMA_Short"].iloc[i]
            long_ma = strategy_df["SMA_Long"].iloc[i]

            if pd.isna(short_ma) or pd.isna(long_ma):
                positions.append(0)
            elif short_ma > long_ma:
                positions.append(1)
            else:
                positions.append(0)

        strategy_df["Position"] = positions

        # Manual signal generation
        signals = [0]
        for i in range(1, len(positions)):
            signal = positions[i] - positions[i - 1]
            signals.append(signal)

        strategy_df["Signal"] = signals

        return strategy_df

    def parameter_tuning(self, short_windows, long_windows):
        close = self._get_close_series()
        records = []
        # Daily returns
        daily_returns = []

        for i in range(len(close)):
            if i == 0:
                daily_returns.append(0)
            else:
                previous_price = close.iloc[i - 1]
                current_price = close.iloc[i]
                daily_return = ( current_price - previous_price) / previous_price
                daily_returns.append(daily_return)
        
        for short_window in short_windows:
            for long_window in long_windows:
                if short_window >= long_window:
                    continue
                strat = self.moving_average_crossover( short_window=short_window,long_window=long_window)
                positions = strat["Position"].tolist()

                strategy_returns = []
                for i in range(len(daily_returns)):
                    if i == 0:
                        strategy_returns.append(0)
                    else:
                        previous_position = positions[i - 1]
                        strategy_return = (
                            daily_returns[i] * previous_position
                        )
                        strategy_returns.append(strategy_return)

                total_return = 1

                for ret in strategy_returns:
                    total_return *= (1 + ret)

                total_return -= 1

                records.append({
                    "short_window": short_window,
                    "long_window": long_window,
                    "total_return": total_return
                })

        if len(records) == 0:
            raise ValueError(
                "No valid short/long window combinations found."
            )

        tuning_df = pd.DataFrame(records)

        tuning_df = tuning_df.sort_values("total_return",ascending=False ).reset_index(drop=True)

        return tuning_df



