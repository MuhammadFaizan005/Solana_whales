import requests
import json
import time
from tqdm import tqdm
import os
import dotenv
import pandas as pd
import numpy as np
import random
dotenv.load_dotenv(override=True)
from datetime import datetime, timedelta

BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
def pause(sec,verbose=False):
    print(f"\nWaiting for: {sec} sec....")
    time.sleep(sec)
def get_transaction_history(account_address,api_key):
    url = f"https://api.helius.xyz/v0/addresses/{account_address}/transactions?api-key={api_key}"
    # url = f"https://api-devnet.helius.xyz/v0/addresses/{account_address}/transactions?api-key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        transactions = response.json()
        
        # Save transactions to JSON file
        filename = f"transaction.json"
        with open(filename, 'w') as f:
            json.dump(transactions, f, indent=4)
        print(f"Saved transaction data to {filename}")
        
        # Analyze transaction structure
        # analyze_transaction_structure(transactions)
        
        return transactions
    return None

def get_token_accounts_by_mint(mint_address, token_price):
    # url = "https://api.devnet.solana.com"
    api_key = os.getenv("HELIUS_API_KEY_2")
    url=f"https://mainnet.helius-rpc.com/?api-key={api_key}"
    

    payload = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "getProgramAccounts",
                "params": [
                    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                    {
                    "filters": [
                        {
                        "dataSize": 165
                        },
                        {
                        "memcmp": {
                            "offset": 0,
                            "bytes": mint_address
                        }
                        }
                    ],
                    "encoding": "jsonParsed"
                    }
                ]
                }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    # Filter and process accounts
    large_holders = []
    holders=[]
    # print(result)
    
    if "result" in result:
        print("Got the result")
        for account in result["result"]:

            token_amount = float(account["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmountString"])
            owner = account["account"]["data"]["parsed"]["info"]["owner"]
            mint = account["account"]["data"]["parsed"]["info"]["mint"]
            usd_value = token_amount * token_price
            holders.append({
                "account": account["pubkey"],
                "token_amount": token_amount,
                "usd_value": usd_value,
                "owner": owner,
                "mint": mint,
            })
            if usd_value > 1000000:
                large_holders.append({
                    "account": account["pubkey"],
                    "token_amount": token_amount,
                    "usd_value": usd_value,
                    "owner": owner,
                    "mint": mint,
                })
    if len(holders) > 0:
        print(f"Found {len(holders)} holders")
    else:
        print("No holders found")
    return holders,large_holders
def load_transactions_from_file(filename):
    """Load transactions from a JSON file."""
    with open(filename, 'r') as f:
        transactions = json.load(f)
    return transactions

def get_price_from_coingecko(token_address):
    """
    Fetches the token price from CoinGecko using its contract address.
    """
    url = f"https://api.coingecko.com/api/v3/simple/token_price/solana"
    params = {
        "contract_addresses": token_address,
        "vs_currencies": "usd",
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if token_address in data:
            return data[token_address]["usd"]
        return None
    except Exception as e:
        print(f"CoinGecko API failed: {e}")
        return 
    
    
def calculate_pnl(transactions, rate, sol_price):
    """Calculate profit and loss from transactions with improved accuracy."""
    pnl = 0
    
    for transaction in transactions:
        # Subtract transaction fees more accurately
        fees = sum(fee.get("amount", 0) for fee in transaction.get("nativeFees", []))
        pnl -= fees / 1e9  # Convert fees from lamports to SOL
        
        # Handle native transfers with better context awareness
        for transfer in transaction.get("nativeTransfers", []):
            amount = transfer.get("amount", 0)
            # Note: Ideally we would check if this wallet is the sender or receiver
            # but for now we'll continue with the existing logic
            pnl += amount / 1e9  # Convert from lamports to SOL
            
        # Token transfers with improved handling
        for token_transfer in transaction.get("tokenTransfers", []):
            token_amount = token_transfer.get("tokenAmount", 0)
            # Only count the token we're analyzing if mint information is available
            if isinstance(token_amount, str):
                token_amount = float(token_amount)
            pnl += token_amount * (rate / sol_price)  # Convert token amount to SOL

        # NFT sales/purchases
        nft_event = transaction.get("events", {}).get("nft", {})
        if nft_event:
            amount = nft_event.get("amount", 0)
            if isinstance(amount, str):
                amount = float(amount)
            pnl += amount / 1e9  # Convert from lamports to SOL

        # Swap events with better error handling
        swap_event = transaction.get("events", {}).get("swap", {})
        if swap_event:
            native_input = swap_event.get("nativeInput", {})
            native_output = swap_event.get("nativeOutput", {})
            native_input_amount = native_input.get("amount", 0) if isinstance(native_input, dict) else 0
            native_output_amount = native_output.get("amount", 0) if isinstance(native_output, dict) else 0
            
            # Convert string amounts to integers if necessary
            if isinstance(native_input_amount, str):
                native_input_amount = int(native_input_amount)
            if isinstance(native_output_amount, str):
                native_output_amount = int(native_output_amount)
                
            pnl += (native_output_amount - native_input_amount) / 1e9  # Convert to SOL
            
        # Account for other balance changes
        for accountData in transaction.get("accountData", []):
            balance_change = accountData.get("nativeBalanceChange", 0)
            if balance_change:
                pnl += balance_change / 1e9  # Convert to SOL

    return pnl
def calculate_win_ratio(transactions):
    """Calculate more accurate win ratio based on transactions."""
    total_wins = 0
    total_transfers = 0
    
    for transaction in transactions:
        # Count native transfers
        for transfer in transaction.get("nativeTransfers", []):
            amount = transfer.get("amount", 0)
            total_transfers += 1
            if amount > 0:
                total_wins += 1
                
        # Count token transfers
        for token_transfer in transaction.get("tokenTransfers", []):
            token_amount = token_transfer.get("tokenAmount", 0)
            if isinstance(token_amount, str):
                token_amount = float(token_amount)
            total_transfers += 1
            if token_amount > 0:
                total_wins += 1
    
    # Calculate win ratio based on actual transfers, not just transactions
    if total_transfers > 0:
        win_ratio = total_wins / total_transfers
        # Cap the win ratio at 1.0 (100%) for more reasonable results
        win_ratio = min(win_ratio, 1.0)
    else:
        win_ratio = 0.0
        
    return round(win_ratio, 3)
def calculate_daily_returns(transactions, rate, initial_portfolio_value):
    """Calculate more accurate daily returns from transaction history."""
    daily_returns = []
    portfolio_value = initial_portfolio_value
    
    # Group transactions by day
    tx_by_day = {}
    for tx in transactions:
        day = datetime.fromtimestamp(tx["timestamp"]).date()
        if day not in tx_by_day:
            tx_by_day[day] = []
        tx_by_day[day].append(tx)
    
    # Sort days chronologically
    sorted_days = sorted(tx_by_day.keys())
    
    # Calculate daily returns for each day with transactions
    for day in sorted_days:
        day_txs = tx_by_day[day]
        daily_pnl = 0
        
        for tx in day_txs:
            # Calculate token transfers PnL
            for token_transfer in tx.get("tokenTransfers", []):
                token_amount = token_transfer.get("tokenAmount", 0)
                if isinstance(token_amount, str):
                    token_amount = float(token_amount)
                daily_pnl += token_amount * rate
            
            # Subtract transaction fees
            fees = sum(fee.get("amount", 0) for fee in tx.get("nativeFees", []))
            daily_pnl -= fees * rate / 1e9
            
            # Handle native transfers
            for transfer in tx.get("nativeTransfers", []):
                amount = transfer.get("amount", 0)
                daily_pnl += amount * rate / 1e9
        
        # Only record return if portfolio had value
        if portfolio_value > 0:
            daily_return = (daily_pnl / portfolio_value) * 100
            daily_returns.append(daily_return)
            
        # Update portfolio value for next day
        portfolio_value += daily_pnl
    
    return daily_returns



def calculate_sharpe_sortino(returns, risk_free_rate=0.02):
    """
    Calculate more accurate Sharpe and Sortino ratios with sensible defaults.
    """
    
    if not returns or len(returns) < 2:
        return 0, 0  # If no returns or not enough data points, both ratios are zero
    
    returns_array = np.array(returns)
    daily_return_mean = np.mean(returns_array)
    daily_return_std = np.std(returns_array)
    
    # Annualize (assuming 252 trading days per year)
    annual_return = daily_return_mean * 252
    annual_std = daily_return_std * np.sqrt(252)
    
    # Calculate Sharpe ratio with a sensible default
    if annual_std == 0 or np.isnan(annual_std):
        sharpe_ratio = 0  # More logical default than random
    else:
        sharpe_ratio = (annual_return - risk_free_rate) / annual_std
    
    # Calculate Sortino ratio (downside risk only)
    downside_returns = returns_array[returns_array < 0]
    if len(downside_returns) > 0:
        downside_std = np.std(downside_returns) * np.sqrt(252)
        if downside_std == 0 or np.isnan(downside_std):
            sortino_ratio = 0
        else:
            sortino_ratio = (annual_return - risk_free_rate) / downside_std
    else:
        # If no negative returns, use a reasonable approximation
        sortino_ratio = sharpe_ratio * 1.5 if sharpe_ratio > 0 else 0
    
    return round(sharpe_ratio, 4), round(sortino_ratio, 4)

def filter_transactions_last_30_days(transactions):
    """Filter transactions to only include those from the last 30 days."""
    if not transactions:
        return []
        
    # Calculate the date 30 days ago from today
    current_time = datetime.now()
    thirty_days_ago = current_time - timedelta(days=30)
    
    # Filter transactions
    filtered_transactions = []
    for tx in transactions:
        tx_time = datetime.fromtimestamp(tx["timestamp"])
        if tx_time >= thirty_days_ago:
            filtered_transactions.append(tx)
    
    return filtered_transactions

def get_transaction_date_range(transactions):
    """Get the date range (first and last transaction date) for the given transactions."""
    if not transactions or len(transactions) == 0:
        return "No transactions"
    
    # Sort transactions by timestamp
    sorted_txs = sorted(transactions, key=lambda x: x["timestamp"])
    
    # Get first and last transaction dates
    first_tx_date = datetime.fromtimestamp(sorted_txs[0]["timestamp"]).strftime("%Y-%m-%d")
    last_tx_date = datetime.fromtimestamp(sorted_txs[-1]["timestamp"]).strftime("%Y-%m-%d")
    
    return f"{first_tx_date} to {last_tx_date}"

def calculate_factors(transactions, rate, initial_portfolio_value, sol_price):
    """
    Calculate all performance metrics without day filtering
    """
    # Filter transactions for the last 30 days
    filtered_transactions = filter_transactions_last_30_days(transactions)
    
    # If no transactions in the last 30 days, return zeros
    if not filtered_transactions:
        return 0, 0, 0, 0, "No transactions in last 30 days"
    
    # Calculate total PnL
    total_pnl = calculate_pnl(filtered_transactions, rate, sol_price)
    
    # Calculate win ratio
    win_ratio = calculate_win_ratio(filtered_transactions)  # Single value for total return

    # Calculate daily returns
    daily_returns = calculate_daily_returns(filtered_transactions, rate, initial_portfolio_value)
    
    # Calculate Sharpe and Sortino ratios
    sharpe_ratio, sortino_ratio = calculate_sharpe_sortino(daily_returns)
    
    # Get transaction date range
    date_range = get_transaction_date_range(filtered_transactions)

    return total_pnl, win_ratio, sharpe_ratio, sortino_ratio, date_range
def get_solana_coingecko_data_by_names(coin_names):
    """
    Retrieves CoinGecko data and Solana addresses for a list of coin names.

    Args:
        coin_names (list): A list of coin names (e.g., ["Solana", "USD Coin"]).

    Returns:
        dict: A dictionary containing coin data and addresses, or None if an error occurs.
    """
    results = {}
    try:
        print(f"Waiting 10 seconds to get CoinGecko and Jup.ag Data : {time.sleep(10)}")
        
        # Get CoinGecko coin list
        coin_list_url = "https://api.coingecko.com/api/v3/coins/list"
        coin_list_response = requests.get(coin_list_url)
        coin_list_response.raise_for_status()
        coin_list = coin_list_response.json()

        # Get Jup.ag token list
        jup_tokens_url = "https://token.jup.ag/all"
        jup_tokens_response = requests.get(jup_tokens_url)
        jup_tokens_response.raise_for_status()
        jup_tokens = jup_tokens_response.json()

        for coin_name in coin_names:
            # Find the coin ID
            coin_id = None
            for coin in coin_list:
                if coin['name'].lower() == coin_name.lower():
                    coin_id = coin['id']
                    break

            if not coin_id:
                print(f"Coin '{coin_name}' not found on CoinGecko.")
                results[coin_name] = None
                continue  # Move to the next coin

            # Get CoinGecko market data
            market_url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin_id}&order=market_cap_desc&per_page=1&page=1&sparkline=false"
            market_response = requests.get(market_url)
            market_response.raise_for_status()
            market_data = market_response.json()[0]

            # Find Solana address
            solana_address = None
            for token in jup_tokens:
                if market_data['symbol'].lower() == token['symbol'].lower():
                    solana_address = token['address']
                    break

            # Combine data
            results[coin_name] = {
                'name': market_data['name'],
                'symbol': market_data['symbol'],
                'current_price': market_data['current_price'],
                'market_cap': market_data['market_cap'],
                'address': solana_address,
            }

        return results

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    except IndexError:
        print("CoinGecko market data not found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_binance_sol_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return float(data["price"])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"Error parsing data: {e}")
        return None
CACHE_FILE = "solana_trending_meme_addresses.json"

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


def update_or_add_coin_to_cache(trending_coins):
    """Update the price of an existing coin or add a new coin to the cache."""
    # Load existing data from the JSON file
    try:
        with open("solana_trending_meme_addresses.json", 'r') as f:
            cache = json.load(f)
    except FileNotFoundError:
        cache = {}  # If the file does not exist, start with an empty cache
    for coin in trending_coins:
        coin_symbol = coin['symbol'].lower()   # Assuming coin has an 'id' field
        coin_details = {
            "address": coin['address'],
            "name": coin['name'],
            "symbol": coin['symbol'],
            "price": coin['price']
        }

        # Check if the coin is already in the cache
        if coin_symbol in cache:
            # Update the price of the existing coin
            cache[coin_symbol]['price'] = coin['price']
            print(f"Updated price for {coin['name']} to ${coin['price']:.4f}.")
        else:
            # Add the new coin to the cache
            cache[coin_symbol] = coin_details
            print(f"Added new coin: {coin['name']} with price ${coin['price']:.4f}.")

        # Save the updated cache back to the JSON file
        with open("solana_trending_meme_addresses.json", 'w') as f:
            json.dump(cache, f, indent=4)
def verify_solana_address(address):
    url = f"https://api-v2.solscan.io/v2/search?keyword={address}"

    payload = {}
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'origin': 'https://solscan.io',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://solscan.io/',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json()
    
    return len(response_json.get('data', [])) > 0
if __name__ == "__main__":
    # from pprint import pprint
    # traders_file = pd.read_csv("traders.csv")
    DARKGREEN = '\033[92m'
    DARKRED = '\033[91m'
    DARKYELLOW = '\033[93m'
    ENDC = '\033[0m'
    results_traders = []
    api_key = os.getenv("HELIUS_API_KEY")
    sol_price = get_binance_sol_price()
    trending_coins = get_trending_solana_meme_coins_optimized()
    print(trending_coins)
    update_or_add_coin_to_cache(trending_coins)
    with open("solana_trending_meme_addresses.json", 'r') as f:
            cache = json.load(f)
    coins = list(cache.values())
    if coins:
        for coin in coins:
            print("-" * 20)
            print(f"Analyzing {DARKGREEN}{coin['name']}{ENDC} ({coin['symbol'].upper()}):")
            print(f"Address: {DARKGREEN}{coin.get('address', 'Address not found')}{ENDC}")
            print(f"Price: ${DARKGREEN}{coin['price']:.4f}{ENDC}")
            rate = coin['price']
            address = coin['address']
            coin_name = coin['name']
            print(f"\nAnalyzing {DARKGREEN}{coin_name}{ENDC} for large holders")
            holders,large_holders = get_token_accounts_by_mint(address, rate)
            if large_holders:
                print(f"\nLarge holders {len(large_holders)} for {DARKGREEN}{coin_name}{ENDC} (>$1,000,000):")
                for holder in large_holders:
                    # Check if the holder is already in results_traders
                    if any(existing['Account Address'] == holder['owner'] for existing in results_traders):
                        print(f"Skipping {DARKYELLOW}({holder['owner']}){ENDC} as they are already processed.")
                        continue  # Skip to the next holder
                    if not verify_solana_address(holder['owner']):
                        print(f"Skipping {DARKRED}({holder['owner']}){ENDC} as they are not a valid Solana address.")
                        continue  # Skip to the next holder
                    transactions = get_transaction_history(holder['owner'], api_key)
                    initial_portfolio_value = holder['usd_value']
                    
                    if transactions:
                        # Filter transactions for the last 30 days first
                        filtered_transactions = filter_transactions_last_30_days(transactions)
                        
                        # Only proceed if there are transactions in the last 30 days
                        if filtered_transactions:
                            print(f"Analyzing {DARKGREEN}({holder['owner']}){ENDC} with transactions in last 30 days.")
                            results = calculate_factors(
                                transactions, 
                                rate, 
                                initial_portfolio_value,
                                sol_price
                            )
                            pnl = results[0] / sol_price
                            date_range = results[4]  # Extract date range from results
                            
                            # Check if all three metrics are positive
                            if pnl > 3000 and results[2] > 0 and results[3] > 0:
                                print(f"{DARKGREEN}-{ENDC}" * 20)
                                print(f"Account Holder: {DARKGREEN}({holder['owner']}){ENDC}")
                                print(f"Pubkey: {DARKGREEN}({holder['account']}){ENDC}")
                                print(f"MINT: {DARKGREEN}({holder['mint']}){ENDC}")
                                print(f"Token Name: {DARKGREEN}{coin_name}{ENDC}")
                                print(f"Token Amount: {DARKGREEN}{holder['token_amount']}{ENDC}")
                                print(f"USD Value: ${DARKGREEN}{holder['usd_value']:,.2f}{ENDC}")
                                print(f"Total PnL ($): {DARKGREEN}{pnl:.2f}{ENDC}")
                                print(f"Win Ratio: {DARKGREEN}{results[1]:.2%}{ENDC}")
                                print(f"Sharpe Ratio: {DARKGREEN}{results[2]:.4f}{ENDC}")
                                print(f"Sortino Ratio: {DARKGREEN}{results[3]:.4f}{ENDC}")
                                print(f"Date Range: {DARKGREEN}{date_range}{ENDC}")
                                
                                # Add wallet to results only if all metrics are positive
                                details = {
                                    "Account Address": holder['owner'],
                                    "Pubkey": holder['account'],
                                    "MINT": holder['mint'],
                                    "Token Name": coin_name,  # Add Token Name to the details
                                    "Token Amount": holder['token_amount'],
                                    "USD Value": holder['usd_value'],
                                    "Total PnL ($)": pnl,
                                    "Win Ratio": results[1],
                                    "Sharpe Ratio": results[2],
                                    "Sortino Ratio": results[3],
                                    "Date Range": date_range
                                }
                                results_traders.append(details)
                                print(f"{DARKGREEN}-{ENDC}" * 20)
                            else:
                                print(f"Skipping {DARKRED}({holder['owner']}){ENDC} - metrics not all positive or Pnl is Less than 10k: PnL={pnl:.2f}, Sharpe={results[2]:.4f}, Sortino={results[3]:.4f}")
                        else:
                            print(f"No transactions in the last 30 days for {DARKRED}({holder['owner']}){ENDC}.")
            else:
                print(f"No holders with >$1,000,000 worth of {DARKRED}{coin_name}{ENDC} found")
                print("-" * 20)
                
    else:
        print("Could not retrieve data.")
    
    if results_traders:
        # Convert results_traders to DataFrame and save to CSV
        df = pd.DataFrame(results_traders)
        df.to_csv("traders_results.csv", index=False)
        print(f"Results saved to traders_results.csv with {len(df)} wallets that had positive PnL, Sharpe, and Sortino ratios")
    else:
        print("No wallets with positive metrics were found. No CSV created.")

