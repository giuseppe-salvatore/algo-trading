Feature: Positions

    Scenario: No positions are open when the simulation starts
        Given I start a new trading session
        Then no positions should be open

    Scenario: A market buy order opens a long position
        Given I start a new trading session
        And I deposit 1000$
        And no open positions with AAPL
        When I submit a market buy order for 10 AAPL stocks
        Then a long position for AAPL should be open

    Scenario: A market sell order opens a short position
        Given I start a new trading session
        And I deposit 1000$
        And no open positions with AAPL
        When I submit a market sell order for 10 AAPL stocks
        Then a short position for AAPL should be open

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

    Scenario: Equity gets updated when a position is open
        Given I start a new trading session
        And I deposit 1000$
        And I have a long position of 20 AAPL stocks bought at 10$
        When the AAPL price moves to 15$
        Then my equity should update to 300$

    Scenario: Equity goes back to balance when a position decreased
        Given I start a new trading session
        And I deposit 1000$
        And I have a long position of 20 AAPL stocks bought at 10$
        When the AAPL price moves to 15$
        Then my equity should update to 300$
        When I sell 10 AAPL stocks
        Then my equity should update to 150$
        And my cash balance should be 950$

    Scenario: Equity goes back to balance when a position is liquidated
        Given I start a new trading session
        And I deposit 1000$
        And I have a long position of 20 AAPL stocks bought at 10$
        When the AAPL price moves to 15$
        Then my equity should update to 300$
        When I sell 20 AAPL stocks
        Then my equity should update to 0$
        And my cash balance should be 1100$

    Scenario: Equity is not updated when a position is already closed
        Given I start a new trading session
        And I deposit 1000$
        And I have a long position of 20 AAPL stocks bought at 10$
        When the AAPL price moves to 15$
        And I close the position
        And the AAPL price moves to 10$
        Then my equity should update to 300$

    Scenario: Equity moves with market value
        Given I start a new trading session
        And I deposit 1000$
        And I have a long position of 20 AAPL stocks bought at 10$
        When the AAPL price moves to 15$
        Then my equity should update to 300$
        When the AAPL price moves to 20$
        Then my equity should update to 400$
        When the AAPL price moves to 0$
        Then my equity should update to 0$