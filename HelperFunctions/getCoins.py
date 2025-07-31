import requests
import time

def get_trending_solana_meme_coins_byName(coinslist,delay=5):
    """Retrieves trending Solana meme coins with addresses, optimized for speed."""
    # Remove cache loading
    # cache = load_cache()
    coins=[]
    print(coinslist)
    # 1. Get all Solana meme coins
    solana_meme_coins_url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=solana-meme-coins"
    try:
        solana_meme_coins_response = requests.get(solana_meme_coins_url)
        solana_meme_coins_response.raise_for_status()
        solana_meme_coins_data = solana_meme_coins_response.json()
        print("Available coins from API:")
        # for solCoin in solana_meme_coins_data:
        #     print(solCoin['name'])
        if coinslist:
            for coin in coinslist:
                for solCoin in solana_meme_coins_data:
                    if (coin.strip().lower() == solCoin['name'].strip().lower() or
                        coin.strip().lower() == solCoin['symbol'].strip().lower()):
                        trending_coin_id = solCoin['id']
                        coin_details_url = f"https://api.coingecko.com/api/v3/coins/{trending_coin_id}"
                        try:
                            print(f"Getting coin details for {solCoin['name']}")
                            coin_details_response = requests.get(coin_details_url)
                            coin_details_response.raise_for_status()
                            coin_details = coin_details_response.json()
                            if 'platforms' in coin_details and 'solana' in coin_details['platforms']:
                                address = coin_details['platforms']['solana']
                            else:
                                address = None
                            # Robust price extraction
                            usd_price = None
                            if 'market_data' in coin_details and 'current_price' in coin_details['market_data']:
                                usd_price = coin_details['market_data']['current_price'].get('usd')
                        except requests.exceptions.RequestException as detail_e:
                            print(f"Error fetching coin details for {trending_coin_id}: {detail_e}")
                            address = None
                            usd_price = None
                        if address:
                            print(f"Appending coin: {solCoin['name']} | symbol: {solCoin['symbol']} | address: {address} | price: {usd_price}")
                            coins.append({
                                'name': solCoin['name'],
                                'symbol': solCoin['symbol'],
                                'address': address,
                                'price': usd_price
                            })
                        print(f"waiting {delay} seconds")
                        time.sleep(delay)
        if coins:
            return coins
    except Exception as e:
        print(f"Got Error While Fetching Coins Details: {e}")
    return coins
