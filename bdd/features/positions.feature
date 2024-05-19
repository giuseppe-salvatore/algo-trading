Feature: Positions

    Scenario: No positions are open when the simulation starts
        Given I start a new trading session
        Then no positions should be open

    Scenario Outline: A market <SIDE> order opens a <DIRECTION> position
        Given I start a new trading session
        And I deposit 1000$
        And no open positions with AAPL
        When I submit a market <SIDE> order for <QUANTITY> AAPL stocks
        Then a <DIRECTION> position for AAPL should be open
        Examples:
            | DIRECTION | SIDE | QUANTITY |
            | long      | buy  | 10       |
            | short     | sell | 10       |

    Scenario: A market sell order on a long position for same quantity, closes the position
        Given I start a new trading session
        And I deposit 1000$
        And no open positions with AAPL
        And I submit a market buy order for 10 AAPL stocks
        When I submit a market sell order for 10 AAPL stocks
        Then the AAPL position should be closed

    Scenario: A market buy order on a short position for same quantity, closes the position
        Given I start a new trading session
        And I deposit 1000$
        And no open positions with AAPL
        And I submit a market sell order for 10 AAPL stocks
        When I submit a market buy order for 10 AAPL stocks
        Then the AAPL position should be closed

    Scenario: Equity doesn't change when no positions are open
        Given I start a new trading session
        And there are no open positions
        Then my equity should be 0$

    Scenario Outline: Equity gets updated when entering a <DIRECTION> position
        Given I start a new trading session
        And I deposit 1000$
        When I enter a <DIRECTION> position of 20 AAPL stocks at <ENTER_PRICE>$ per share
        Then my equity should update to <EXPECTED_EQUITY>$
        Examples:
            | DIRECTION | ENTER_PRICE | EXPECTED_EQUITY |
            | long      | 10          | 200             |
            | short     | 10          | 200             |

    Scenario Outline: Equity gets updated when stock price changes and a <DIRECTION> position is already open
        Given I start a new trading session
        And I deposit 1000$
        And I entered a <DIRECTION> position of 20 AAPL stocks at <ENTER_PRICE>$ per share
        When the AAPL price moves to <TARGET_PRICE>$
        Then my equity should update to <EXPECTED_EQUITY>$
        Examples:
            | DIRECTION | ENTER_PRICE | TARGET_PRICE | EXPECTED_EQUITY |
            | long      | 10          | 15           | 300             |
            | short     | 10          | 5            | 300             |

    Scenario Outline: Equity goes back to balance when a <DIRECTION> position decreased
        Given I start a new trading session
        And I deposit 1000$
        And I entered a <DIRECTION> position of 20 AAPL stocks at <ENTER_PRICE>$ per share
        When the AAPL price moves to <TARGET_PRICE_1>$
        Then my equity should update to <EXPECTED_EQUITY_1>$
        When I <SIDE> 10 AAPL stocks
        Then my equity should update to <EXPECTED_EQUITY_2>$
        And my cash balance should be <CASH_BALANCE>$
        Examples:
            | DIRECTION | ENTER_PRICE | TARGET_PRICE_1 | EXPECTED_EQUITY_1 | SIDE | EXPECTED_EQUITY_2 | CASH_BALANCE |
            | long      | 10          | 15             | 300               | sell | 150               | 950          |
            | short     | 10          | 5              | 300               | buy  | 150               | 950          |
            | long      | 12          | 20             | 400               | sell | 200               | 960          |
            | short     | 12          | 4              | 400               | buy  | 200               | 960          |

    Scenario Outline: Equity goes back to balance when a long position is liquidated
        Given I start a new trading session
        And I deposit 1000$
        And I entered a <DIRECTION> position of 20 AAPL stocks at <ENTER_PRICE>$ per share
        When the AAPL price moves to <TARGET_PRICE_1>$
        Then my equity should update to <EXPECTED_EQUITY_1>$
        When I <SIDE> 20 AAPL stocks
        Then my equity should update to 0$
        And my cash balance should be <CASH_BALANCE>$
        Examples:
            | DIRECTION | ENTER_PRICE | TARGET_PRICE_1 | EXPECTED_EQUITY_1 | SIDE | CASH_BALANCE |
            | long      | 10          | 15             | 300               | sell | 1100         |
            | short     | 10          | 5              | 300               | buy  | 1100         |

    Scenario Outline: Equity is not updated when a <DIRECTION> position is already closed
        Given I start a new trading session
        And I deposit 1000$
        And I entered a long position of 20 AAPL stocks at 10$ per share
        When the AAPL price moves to <TARGET_PRICE_1>$
        And I close the position
        And the AAPL price moves to <TARGET_PRICE_2>$
        Then my equity should update to 0$
        Examples:
            | DIRECTION | TARGET_PRICE_1 | TARGET_PRICE_2 |
            | long      | 15             | 10             |
            | short     | 5              | 10             |

    Scenario Outline: Equity moves with market value
        Given I start a new trading session
        And I deposit 1000$
        And I entered a <DIRECTION> position of 20 AAPL stocks at <ENTER_PRICE>$ per share
        When the AAPL price moves to <TARGET_PRICE_1>$
        Then my equity should update to <EXPECTED_EQUITY_1>$
        When the AAPL price moves to <TARGET_PRICE_2>$
        Then my equity should update to <EXPECTED_EQUITY_2>$
        Examples:
            | DIRECTION | ENTER_PRICE | TARGET_PRICE_1 | EXPECTED_EQUITY_1 | TARGET_PRICE_2 | EXPECTED_EQUITY_2 |
            | long      | 10          | 20             | 400               | 5              | 100               |
            | short     | 10          | 0              | 400               | 15             | 100               |