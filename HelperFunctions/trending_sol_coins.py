import requests
import time
def get_trending_solana_meme_coins_optimized(delay=5):
    """Retrieves trending Solana meme coins with addresses, optimized for speed."""
    # Remove cache loading
    # cache = load_cache()

    # 1. Get all Solana meme coins
    solana_meme_coins_url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=solana-meme-coins"
    try:
        solana_meme_coins_response = requests.get(solana_meme_coins_url)
        solana_meme_coins_response.raise_for_status()
        solana_meme_coins_data = solana_meme_coins_response.json()
        solana_meme_coins_ids = {coin['id']: coin for coin in solana_meme_coins_data} #create a dictionary for fast lookup.

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Solana meme coins: {e}")
        return None

    # 2. Get trending coins
    trending_url = "https://api.coingecko.com/api/v3/search/trending"
    try:
        trending_response = requests.get(trending_url)
        trending_response.raise_for_status()
        trending_data = trending_response.json()
        trending_coins = trending_data['coins']

    except requests.exceptions.RequestException as e:
        print(f"Error fetching trending coins: {e}")
        return None

    solana_trending_meme = []

    # 3. Find trending Solana meme coins and get details
    for trending_coin in trending_coins:
        trending_coin_id = trending_coin['item']['id']
        if trending_coin_id in solana_meme_coins_ids:
            # Remove cache check
            # if trending_coin_id in cache:
            #     address = cache[trending_coin_id]
            #     print(f"Address for {trending_coin['item']['name']} from cache.")
            # else:
                coin_details_url = f"https://api.coingecko.com/api/v3/coins/{trending_coin_id}"
                try:
                    print(f"Getting coin details for {trending_coin['item']['name']}")
                    coin_details_response = requests.get(coin_details_url)
                    coin_details_response.raise_for_status()
                    coin_details = coin_details_response.json()
                    if 'platforms' in coin_details and 'solana' in coin_details['platforms']:
                        address = coin_details['platforms']['solana']
                        # Remove cache saving
                        # cache[trending_coin_id] = address
                        # save_cache(cache)
                    else:
                        address = None
                except requests.exceptions.RequestException as detail_e:
                    print(f"Error fetching coin details for {trending_coin_id}: {detail_e}")
                    address = None

                if address:
                    solana_trending_meme.append({
                        'name': trending_coin['item']['name'],
                        'symbol': trending_coin['item']['symbol'],
                        'address': address,
                        'price': solana_meme_coins_ids[trending_coin_id]['current_price']
                    })
                print(f"waiting {delay} seconds")
                time.sleep(delay)

    return solana_trending_meme
