from .... import api_proxy

if __name__ == "__main__":
    paper_account = api_proxy.TradeApiProxy("paper")
    assets = paper_account.api.list_assets()
    print(assets)