# The Simple Scalping Strategy #

## Summary ##
The simple scalping strategy consists in taking positions in equities that have high volatility and can make sudden changes (we are looking at least 2-3%) and exit from those positions in a very short amount of time, once the upward or downard trend is exausted.

## Optimal Stocks ##
Use the scanner feature of TradingView and search for the stocks that have
- Market Cap > 10B
- Average Volume on 90 days > 500k

## Charts and Indicators ##
We are going to be using 1 and 5 minutes candles charts to analyse the entry/exit to/from the positions
- 5 EMA
- 5 SMMA
- Bollinger Bands
- RSI

## Chart Analysis ##
Analyse the 5 mins period chart and trade on 1 min period. The 5 mins period will tell us what we can do on the 1 min
1. If on 5 min chart prices and BB are moving sideways => make positions up/down on 1 min chart
2. If on 5 min chart prices and BB are moving upward => make only long positions on 1 min chart
3. If on 5 min chart prices and BB are moving downward => make only short positions on 1 min chart

## Buying Signals ##
- 5 EMA crosses above 5 SMMA
- RSI > 50
- BB is Sloping Up
- Exit when 1:1 R2R (1:2 R2R on cases 2 and 3)

## Selling Signals ##
- 5 EMA crosses below 5 SMMA
- RSI < 50
- BB is Sloping Down
- Exit when 1:1 R2R (1:2 R2R on cases 2 and 3)
