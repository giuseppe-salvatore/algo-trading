

class SimpleScalping():

    def __init__(self, symbol):
        self.symbol = symbol
        self.fiveMinsChartStatus = "NONE"

    def isFiveMinsChartGoingUp(self):
        pass

    def isFiveMinsChartGoingDown(self):
        pass

    def isFiveMinsChartGoingSideway(self):
        pass

    def isFiveMinsChartBBExpanding(self):
        pass

    def isFiveMinsChartBBContracting(self):
        pass

    def update(self):
        pass
        # Get latest values for 5 mins chart
        # Analyse the chart:
        # - Calculate the Bollinger Bands
        # - Check where those are going 
        # - Check if they have changed compared to the previous status
        # - The result could be: they are going up, down, sideways, unrecognised, expanding, contracting and it could have been updated

        # Based on the result of the above we can decide if we want to trade or exit if we are already in a trade
    
    