from CoreFunctions.SolPriceVsCoins import glsmco
from CoreFunctions.holdersBySol import SolScan_holders_fetch  as get_holders
from pprint import pprint
from tqdm import tqdm
from HelperFunctions.AccountCheck import AccountVerification
from CoreFunctions.transactionByHelius import get_transaction
from CoreFunctions.factors import calculate_factors
from dotenv import load_dotenv
import os
from tqdm import tqdm
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
load_dotenv(override=True)
api_key = os.getenv('HELIUS_API_KEY_1')
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'

def process_holder(holder, results, token_price, coin, PNL, verbose=False):
    owner = holder['owner']
    tokenHoldingPrice = holder['TokenAmount']
    verifyFlag = AccountVerification(owner)
    if verifyFlag:
        transactions = get_transaction(owner, api_key)
        if transactions:
            if verbose:
                print(f"\nAnalyzing {GREEN}({holder['owner']}){ENDC} with transactions in last 30 days.")
            resultsFactors = calculate_factors(
                transactions, 
                token_price, 
                tokenHoldingPrice,
                results['Sol']
            )
            pnl = resultsFactors[0] / results['Sol']
            date_range = resultsFactors[4]
            if pnl > PNL and resultsFactors[2] > 0 and resultsFactors[3] > 0:
                details = {
                    "Account Address": holder['owner'],
                    "Token Name": coin['name'],
                    "Token Amount": tokenHoldingPrice,
                    "Total PnL ($)": pnl,
                    "Win Ratio": resultsFactors[1],
                    "Sharpe Ratio": resultsFactors[2],
                    "Sortino Ratio": resultsFactors[3],
                    "Date Range": date_range
                }
                return details
    return None

def run_treads_Transactions_parallel(results_traders, results, holders, token_price, coin, PNL, verbose=False, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_holder, holder, results, token_price, coin, PNL, verbose)
            for holder in holders
        ]
        for future in tqdm(as_completed(futures), total=len(holders), desc="Holders (threaded)", colour="YELLOW"):
            result = future.result()
            if result:
                results_traders.append(result)

def main(verbose= False,StartPage=0, EndPage = 10,PNL=3000,rangeStart=50000,rangeEnd=100000,coinslist=[]):
    print(f"Got Request for \nStartPage:{StartPage}\nEndPage:{EndPage}\nrangeStart:{rangeStart}\nrangeEnd:{rangeEnd}\nPNL:{PNL}")
    results_traders = []
    results = glsmco(coinslist)
    holders = []
    if results:
        if 'MemeCoins' in results:
            coins = results['MemeCoins']
            if coins:
                if verbose:
                    print(f"Got Meme Coins : {GREEN}{len(coins)}{ENDC}")
                if verbose:
                    pprint(coins)
                for coin in tqdm(coins,colour="GREEN", desc="Coins"):
                    if verbose:
                        print(f"\nWorking on Coin: {GREEN}{coin['name']}{ENDC}\nAddress:{YELLOW} {coin['address']}{ENDC}")
                    token_price = coin['price']
                    token_address = coin['address']
                    try:
                        holderslist = get_holders(address=token_address, token_price=token_price,StartPage = StartPage, EndPage=EndPage,rangeStart= rangeStart,rangeEnd=rangeEnd)
                        if holderslist:
                            holders.extend(holderslist)
                    except Exception as e:
                        if verbose:
                            print(f"\nFailed to Get Holders From Solscan : {e}")
            # Run threaded processing for holders
            if holders:
                if verbose:
                    print(f"Got Holders: {len(holders)}")
                run_treads_Transactions_parallel(results_traders, results, holders, token_price, coin, PNL, verbose, max_workers=5)
        else:
            if verbose:
                print(f"{RED}No Results {ENDC}")
    # Save results
    if results_traders:
        df = pd.DataFrame(results_traders)
        df.to_csv('Traders.csv', index=False)
        print(f"Saved {len(results_traders)} traders to Traders.csv")

if __name__ == ("__main__"):
    main(
        StartPage=0,
        EndPage=50,
        PNL=5000,
        rangeStart=50000,
        rangeEnd=300000,
        coinslist = [
            "FARTCOIN",
            # "TROLL",
            # "Pudgy Penguins",
            ]
        )