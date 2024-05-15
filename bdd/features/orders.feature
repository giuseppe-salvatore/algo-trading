Feature: Order managment

    Scenario: Placing a bracket limit order
        Given I submit a bracket limit order to buy 10 AAPL stocks
        When the limit price is hit
        Then the order is executed
        And a long position with 10 AAPL is open
        And the take profit leg is converted in a limit order
        And the stop loss leg is converted in a stop order

    Scenario: Placing a bracket market order
        Given I submit a bracket market order to buy 10 AAPL stocks
        And a long position with 10 AAPL is open
        When the stock price goes above the limit price
        Then the limit leg order is executed
        And the position is closed
        And the stop order is cancelled

    Scenario: Placing a buy market order below the available cash balance
        Given I have 1000$ available in my cash balance
        And no open positions with AAPL
        And the AAPL stock price is 20$ per unit
        When I submit a market buy order for 10 AAPL stocks
        Then the order should be executed
        And my cash balance should be 800$

    Scenario: Placing a sell market order below the available cash balance
        Given I have 1000$ available in my cash balance
        And no open positions with AAPL
        And the AAPL stock price is 20$ per unit
        When I submit a market sell order for 10 AAPL stocks
        Then the order should be executed
        And my cash balance should be 800$

    Scenario: Placing a buy market order above the available cash balance
        Given I have 1000$ available in my cash balance
        And the AAPL stock price is 200$ per unit
        When I submit a market buy order for 10 AAPL stocks
        Then the order should be rejected
        And my cash balance should be 1000$

    Scenario: Placing a sell market order above the available cash balance
        Given I have 1000$ available in my cash balance
        And the AAPL stock price is 200$ per unit
        When I submit a market buy order for 10 AAPL stocks
        Then the order should be rejected
        And my cash balance should be 1000$

