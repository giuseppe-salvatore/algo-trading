Feature: Order managment
    

    Scenario: Placing a bracket limit order
        Given I submit a bracket limit order to buy 10 AAPL stocks

        When the limit price is hit

	    Then the order is executed
	    And a long position with 10 AAPL is open
	    And the take profit leg is coverted in a limit order
	    And the stop loss leg is converted in a stop order

    Scenario: Placing a bracket market order
        Given I submit a bracket market order to buy 10 AAPL stocks
        And a long position with 10 AAPL is open

        When the stock price goes above the limit price

        Then the limit leg order is executed
        And the position is closed
        And the stop order is cancelled
