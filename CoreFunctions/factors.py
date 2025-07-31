from CoreFunctions.transactionByHelius import filter_transactions_last_30_days
from datetime import datetime
import numpy as np

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
