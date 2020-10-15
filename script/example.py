from lib.util.logger import log
from lib.trading.alpaca import AlpacaTrading

proxy = AlpacaTrading()


def get_asset_data():
    assets = proxy.api.list_assets()
    total_asset_count = 0
    active_asset_count = 0
    shortable_asset_count = 0
    tradable_asset_count = 0

    targets = []

    print("symbol,tradable,shortable,price")
    for asset in assets:
        try:
            total_asset_count += 1

            if asset.status == 'active':
                active_asset_count += 1

            if asset.tradable is True:
                tradable_asset_count += 1

            price = str(proxy.get_quote(asset.symbol).askprice)
            if asset.status == 'active' and asset.tradable is True:
                print(str(asset.symbol) + ",", end="")
                print(str(asset.tradable) + ",", end="")
                print(str(asset.shortable) + ",", end="")
                if asset.shortable is True:
                    shortable_asset_count += 1
                targets.append(asset.stymbol)
            print(price)
            # ass = proxy.api.get_asset(asset.symbol)
        except KeyboardInterrupt as ki:
            log.error(ki)
            break
        except Exception as e:
            log.error(e)

    target_string = ""
    for target in targets:
        target_string += target + ","

    target_string = target_string[:-1]

    print("Total number of assets: " + str(total_asset_count))
    print("Active assets: " + str(active_asset_count))
    print("Shortable assets: " + str(shortable_asset_count))
    print("Tradable assets: " + str(tradable_asset_count))


if __name__ == "__main__":

    # get_asset_data()
    log.info(proxy.api.polygon.news('MSFT'))
    # print(proxy.api.polygon.gainers_losers("gainers"))
