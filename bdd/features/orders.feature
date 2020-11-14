Feature: Order managment
    A site where you can publish your articles.

    Scenario: Placing a bracket limit order
        Given I place a bracket limit order to buy 10 AAPL stocks

        When the limit price is hit

	    Then the order is executed
	    And a long position with 10 AAPL is open
	    And the take profit leg is coverted in a limit order
	    And the stop loss leg is converted in a stop order
