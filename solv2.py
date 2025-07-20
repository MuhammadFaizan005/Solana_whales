import requests
import json
import numpy as np
from datetime import datetime
import statistics

url = "https://api-v2.solscan.io/v2/account/transaction?address=F7RkX6Y1qTfBqoX5oHoZEgrG1Dpy55UZ3GfWwPbM58nQ&page_size=10"

payload = ""
headers = {
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'en-US,en;q=0.9',
  'if-none-match': 'W/"21a8-gQn/xm+X5A+ZE1KRe5+y98fWriI"',
  'origin': 'https://solscan.io',
  'priority': 'u=1, i',
  'referer': 'https://solscan.io/',
  'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
  'Cookie': '_ga=GA1.1.509847261.1750787802; _ga_PS3V7B7KV0=GS2.1.s1751127788$o3$g1$t1751128175$j60$l0$h0'
}

def calculate_pnl(transactions):
    """
    Calculate Profit and Loss (PnL) from transaction data
    """
    total_pnl = 0
    sol_price = 151.77889238002479  # Current SOL price from metadata
    
    for tx in transactions:
        # Convert sol_value from lamports to SOL (1 SOL = 1e9 lamports)
        sol_amount = float(tx.get('sol_value', 0)) / 1e9
        
        # Calculate USD value
        usd_value = sol_amount * sol_price
        
        # For this example, we'll consider positive sol_value as profit
        # In a real scenario, you'd need to determine buy/sell transactions
        if sol_amount > 0:
            total_pnl += usd_value
        else:
            total_pnl -= abs(usd_value)
    
    return total_pnl

def calculate_win_ratio(transactions):
    """
    Calculate Win Ratio (percentage of profitable transactions)
    """
    if not transactions:
        return 0
    
    profitable_txs = 0
    total_txs = len(transactions)
    
    for tx in transactions:
        sol_amount = float(tx.get('sol_value', 0)) / 1e9
        
        # Consider transaction profitable if positive sol_value
        # In reality, you'd need to track actual buy/sell prices
        if sol_amount > 0:
            profitable_txs += 1
    
    win_ratio = (profitable_txs / total_txs) * 100 if total_txs > 0 else 0
    return round(win_ratio, 2)

def calculate_sharpe_ratio(transactions, risk_free_rate=0.02):
    """
    Calculate Sharpe Ratio (excess return per unit of risk)
    """
    if len(transactions) < 2:
        return 0
    
    # Calculate daily returns
    returns = []
    sol_price = 151.77889238002479
    
    for tx in transactions:
        sol_amount = float(tx.get('sol_value', 0)) / 1e9
        usd_value = sol_amount * sol_price
        returns.append(usd_value)
    
    if not returns:
        return 0
    
    # Calculate average return and standard deviation
    avg_return = np.mean(returns)
    std_return = np.std(returns)
    
    if std_return == 0:
        return 0
    
    # Annualize (assuming daily data)
    annualized_return = avg_return * 365
    annualized_std = std_return * np.sqrt(365)
    
    # Calculate Sharpe ratio
    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_std
    return round(sharpe_ratio, 4)

def calculate_sortino_ratio(transactions, risk_free_rate=0.02):
    """
    Calculate Sortino Ratio (excess return per unit of downside risk)
    """
    if len(transactions) < 2:
        return 0
    
    # Calculate daily returns
    returns = []
    sol_price = 151.77889238002479
    
    for tx in transactions:
        sol_amount = float(tx.get('sol_value', 0)) / 1e9
        usd_value = sol_amount * sol_price
        returns.append(usd_value)
    
    if not returns:
        return 0
    
    # Calculate average return
    avg_return = np.mean(returns)
    
    # Calculate downside deviation (only negative returns)
    negative_returns = [r for r in returns if r < avg_return]
    
    if not negative_returns:
        return float('inf')  # No downside risk
    
    downside_deviation = np.std(negative_returns)
    
    if downside_deviation == 0:
        return 0
    
    # Annualize
    annualized_return = avg_return * 365
    annualized_downside = downside_deviation * np.sqrt(365)
    
    # Calculate Sortino ratio
    sortino_ratio = (annualized_return - risk_free_rate) / annualized_downside
    return round(sortino_ratio, 4)

def calculate_date_range(transactions):
    """
    Calculate the date range of transactions
    """
    if not transactions:
        return None, None
    
    timestamps = []
    for tx in transactions:
        block_time = tx.get('blockTime')
        if block_time:
            timestamps.append(block_time)
    
    if not timestamps:
        return None, None
    
    # Convert Unix timestamps to datetime
    start_date = datetime.fromtimestamp(min(timestamps))
    end_date = datetime.fromtimestamp(max(timestamps))
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def analyze_transactions(transactions_data):
    """
    Main function to analyze all metrics from transaction data
    """
    if not transactions_data or 'transactions' not in transactions_data:
        return None
    
    transactions = transactions_data['transactions']
    
    # Calculate all metrics
    pnl = calculate_pnl(transactions)
    win_ratio = calculate_win_ratio(transactions)
    sharpe_ratio = calculate_sharpe_ratio(transactions)
    sortino_ratio = calculate_sortino_ratio(transactions)
    start_date, end_date = calculate_date_range(transactions)
    
    results = {
        'pnl_usd': pnl,
        'win_ratio_percent': win_ratio,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'date_range': {
            'start_date': start_date,
            'end_date': end_date
        },
        'total_transactions': len(transactions)
    }
    
    return results

# Make the API request and analyze the data
response = requests.request("GET", url, headers=headers, data=payload)

if response.status_code == 200:
    try:
        data = response.json()
        print("API Response Structure:")
        print(f"Keys in response: {list(data.keys())}")
        if 'data' in data:
            print(f"Keys in data: {list(data['data'].keys())}")
        if 'data' in data and 'transactions' in data['data']:
            print(f"Number of transactions: {len(data['data']['transactions'])}")
        
        results = analyze_transactions(data.get('data', data))
        
        if results:
            print("\n=== Transaction Analysis Results ===")
            print(f"Total PnL: ${results['pnl_usd']:,.2f}")
            print(f"Win Ratio: {results['win_ratio_percent']}%")
            print(f"Sharpe Ratio: {results['sharpe_ratio']}")
            print(f"Sortino Ratio: {results['sortino_ratio']}")
            print(f"Date Range: {results['date_range']['start_date']} to {results['date_range']['end_date']}")
            print(f"Total Transactions: {results['total_transactions']}")
        else:
            print("No transaction data found")
            
    except json.JSONDecodeError:
        print("Failed to parse JSON response")
else:
    print(f"API request failed with status code: {response.status_code}")
    print(response.text)
