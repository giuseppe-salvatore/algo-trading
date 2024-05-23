Feature: Fractional Shares Handling

    Scenario: Buying long fractional shares
        Given I start a new trading session
        And I deposit 1000$
        And the AAPL price moves to 10$
        When I submit a market buy order for 10.5 AAPL stocks
        Then the AAPL position should be opened with 10.5 shares
        And my cash balance should be 895$

    Scenario: Selling short fractional shares
        Given I start a new trading session
        And I deposit 1000$
        And the AAPL price moves to 10$
        When I submit a market buy order for 10.5 AAPL stocks
        Then the AAPL position should be opened with 10.5 shares
        And my cash balance should be 895$