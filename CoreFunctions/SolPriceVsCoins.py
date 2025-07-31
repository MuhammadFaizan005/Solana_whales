from HelperFunctions.solprice import get_binance_sol_price
from HelperFunctions.trending_sol_coins import get_trending_solana_meme_coins_optimized
def glsmco():
    sol_price = get_binance_sol_price()
    trending_coins = get_trending_solana_meme_coins_optimized()
    return {
        "Sol": sol_price,
        "MemeCoins" : trending_coins
    }