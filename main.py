from CoreFunctions.SolPriceVsCoins import glsmco
from CoreFunctions.holdersBySol import SolScan_holders_fetch  as get_holders
from pprint import pprint
from tqdm import tqdm
from HelperFunctions.AccountCheck import AccountVerification

BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'


def main(verbose= False, pages = 0):
    results = glsmco()
    if results:
        if 'MemeCoins' in results:
            coins = results['MemeCoins']
            if len(coins)!=0:
                print(f"Got Meme Coins : {GREEN}{len(coins)}{ENDC}")
                if verbose:
                    pprint(coins)
                for coin in coins:
                    print(f"Working on Coin: {GREEN}{coin['name']}{ENDC}\nAddress:{YELLOW} {coin['address']}{ENDC}")
                    token_price = coin['price']
                    token_address = coin['address']
                    for i in range(pages):
                        try:
                            holders = get_holders(address=token_address, token_price=token_price)
                        except Exception as e:
                            print(f"Failed to Get Holders From Solscan : {e}")
                        if holders:
                            for holder in holders:
                                owner = holder['owner']
                                tokenHoldingPrice = holder['TokenAmount']
                                verifyFlag = AccountVerification(holder)
                                # if verifyFlag:


        else:
            print(f"{RED}No Results {ENDC}")
if __name__ == ("__main__"):
    main(pages=10)