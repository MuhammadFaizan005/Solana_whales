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
load_dotenv(override=True)
api_key = os.getenv('HELIUS_API_KEY_1')
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'

def run_treads_Transactions(results_traders,results,holders,token_price,coin,PNL,verbose=False):
    for holder in tqdm(holders, colour="YELLOW", desc="Holders"):
                owner = holder['owner']
                tokenHoldingPrice = holder['TokenAmount']
                verifyFlag = AccountVerification(owner)
                if verifyFlag:
                    transactions = get_transaction(owner,api_key)
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
                        date_range = resultsFactors[4]  # Extract date range from results
                                            
                                            # Check if all three metrics are positive
                        if pnl > PNL and resultsFactors[2] > 0 and resultsFactors[3] > 0:
                            print(f"{GREEN}-{ENDC}" * 20)
                            print(f"Account Holder: {GREEN}({holder['owner']}){ENDC}")
                            if verbose:
                                print(f"Token Name: {GREEN}{coin['name']}{ENDC}")
                                print(f"Token Amount: {GREEN}{tokenHoldingPrice}{ENDC}")
                                print(f"Total PnL ($): {GREEN}{pnl:.2f}{ENDC}")
                                print(f"Win Ratio: {GREEN}{resultsFactors[1]:.2%}{ENDC}")
                                print(f"Sharpe Ratio: {GREEN}{resultsFactors[2]:.4f}{ENDC}")
                                print(f"Sortino Ratio: {GREEN}{resultsFactors[3]:.4f}{ENDC}")
                                print(f"Date Range: {GREEN}{date_range}{ENDC}")

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
                            results_traders.append(details)
                            print(f"{GREEN}-{ENDC}" * 20)
                        else:
                            if verbose:
                                print(f"Skipping {RED}({holder['owner']}){ENDC} - metrics not all positive or {PNL} is Less than 3k: PnL={pnl:.2f}, Sharpe={resultsFactors[2]:.4f}, Sortino={resultsFactors[3]:.4f}")
                    else:
                        if verbose:
                            print(f"No transactions in the last 30 days for {RED}({holder['owner']}){ENDC}.")
                else:
                    if verbose:
                        print(f"Verification Failed: {owner}")
        
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
                    
                        
        else:
            if verbose:
                print(f"{RED}No Results {ENDC}")
        
        if holders:
            if verbose:
                print(f"Got Holders: {len(holders)}")
            for holder in tqdm(holders, colour="YELLOW", desc="Holders"):
                owner = holder['owner']
                tokenHoldingPrice = holder['TokenAmount']
                verifyFlag = AccountVerification(owner)
                if verifyFlag:
                    transactions = get_transaction(owner,api_key)
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
                        date_range = resultsFactors[4]  # Extract date range from results
                                            
                                            # Check if all three metrics are positive
                        if pnl > PNL and resultsFactors[2] > 0 and resultsFactors[3] > 0:
                            print(f"{GREEN}-{ENDC}" * 20)
                            print(f"Account Holder: {GREEN}({holder['owner']}){ENDC}")
                            if verbose:
                                print(f"Token Name: {GREEN}{coin['name']}{ENDC}")
                                print(f"Token Amount: {GREEN}{tokenHoldingPrice}{ENDC}")
                                print(f"Total PnL ($): {GREEN}{pnl:.2f}{ENDC}")
                                print(f"Win Ratio: {GREEN}{resultsFactors[1]:.2%}{ENDC}")
                                print(f"Sharpe Ratio: {GREEN}{resultsFactors[2]:.4f}{ENDC}")
                                print(f"Sortino Ratio: {GREEN}{resultsFactors[3]:.4f}{ENDC}")
                                print(f"Date Range: {GREEN}{date_range}{ENDC}")

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
                            results_traders.append(details)
                            print(f"{GREEN}-{ENDC}" * 20)
                        else:
                            if verbose:
                                print(f"Skipping {RED}({holder['owner']}){ENDC} - metrics not all positive or {PNL} is Less than 3k: PnL={pnl:.2f}, Sharpe={resultsFactors[2]:.4f}, Sortino={resultsFactors[3]:.4f}")
                    else:
                        if verbose:
                            print(f"No transactions in the last 30 days for {RED}({holder['owner']}){ENDC}.")
                else:
                    if verbose:
                        print(f"Verification Failed: {owner}")
        
        else:
            if verbose:
                print(f"{RED}Got No Holders{ENDC}")
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