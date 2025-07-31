import requests
import json
from datetime import datetime, timedelta

def get_transaction_history(account_address,api_key):
    url = f"https://api.helius.xyz/v0/addresses/{account_address}/transactions?api-key={api_key}"
    # url = f"https://api-devnet.helius.xyz/v0/addresses/{account_address}/transactions?api-key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        transactions = response.json()
        
        # Save transactions to JSON file
        # filename = f"transaction.json"
        # with open(filename, 'w') as f:
        #     json.dump(transactions, f, indent=4)
        # print(f"Saved transaction data to {filename}")
        return transactions
    return None

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

def get_transaction(address,api_key):
    transactions = get_transaction_history(address,api_key)
    if transactions:
        filtered_transactions = filter_transactions_last_30_days(transactions)
        return filtered_transactions
    else:
        print("No transactions found")
        return []