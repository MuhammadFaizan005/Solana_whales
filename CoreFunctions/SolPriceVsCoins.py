from HelperFunctions.solprice import get_binance_sol_price
from HelperFunctions.trending_sol_coins import get_trending_solana_meme_coins_optimized
from HelperFunctions.getCoins import get_trending_solana_meme_coins_byName as FetchWithName
def glsmco(coinslist=[]):
    sol_price = get_binance_sol_price()
    if not coinslist:
        trending_coins = get_trending_solana_meme_coins_optimized()
    else:
        trending_coins = FetchWithName(coinslist)
    return {
        "Sol": sol_price,
        "MemeCoins" : trending_coins
    }