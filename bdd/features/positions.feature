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