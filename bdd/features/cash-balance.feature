Feature: Cash balance

    Scenario: Initial balance
        Given I start trading AAPL stocks
        Then my cash balance should be 0$

    Scenario: Deposit amount
        Given I start trading AAPL stocks
        When I deposit 100$
        Then my cash balance should be 100$ 

    Scenario: Withdraw amount smaller than cash balance
        Given I start trading AAPL stocks
        When I deposit 1000$
        And I withdraw 50$
        Then my cash balance should be 950$ 

    Scenario: Withdraw amount bigger than cash balance
        Given I start trading AAPL stocks
        When I deposit 1000$
        And I withdraw 1050$
        Then my cash balance should be 1000$
        And I should receive an error message

    Scenario: Reset trading platform
        Given I start trading AAPL stocks
        When I deposit 1000$
        And I reset the trading platform
        Then my cash balance should be 0$

    Scenario: Multiple deposits
        Given I start trading AAPL stocks
        When I deposit 1000$
        Then my cash balance should be 1000$
        When I deposit 1500$
        Then my cash balance should be 2500$