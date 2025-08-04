# Solana Whales

A Python tool to discover and analyze top Solana meme coin holders ("whales") based on on-chain data, trading performance, and custom filters. The program fetches trending meme coins, retrieves their holders, analyzes their transaction history, and outputs a CSV of high-performing wallets.

## Features
- Fetches trending Solana meme coins and their on-chain holders
- Filters holders by token value and custom ranges
- Analyzes each holder's transaction history for:
  - Profit & Loss (PnL)
  - Win ratio
  - Sharpe and Sortino ratios
  - Date range of activity
- Multi-threaded for fast processing
- Outputs results to `Traders.csv`

## Requirements
- Python 3.8+
- [Helius API Key](https://helius.xyz/)
- [CoinGecko API](public, no key required)
- Solscan API (public, no key required)

### Python Packages
Install dependencies with:
```bash
pip install -r requirement.txt
```

## Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/MuhammadFaizan005/Solana_whales.git
   cd Solana_whales
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirement.txt
   ```
3. **Configure environment variables:**
   - Create a `.env` file in the project root with your Helius API key:
     ```env
     HELIUS_API_KEY_1=your_helius_api_key_here
     ```

## Usage
Run the main script with your desired parameters:
```bash
python main.py
```

You can customize the following parameters in `main.py`:
- `StartPage` / `EndPage`: Range of pages to fetch holders from Solscan
- `PNL`: Minimum profit and loss threshold for filtering whales
- `rangeStart` / `rangeEnd`: Minimum and maximum USD value of token holdings
- `coinslist`: List of meme coin names or symbols to analyze (see CoinGecko's Solana meme coins for valid names)

Example (edit at the bottom of `main.py`):
```python
main(
    StartPage=0,
    EndPage=50,
    PNL=5000,
    rangeStart=50000,
    rangeEnd=300000,
    coinslist=[
        "FARTCOIN",
        "TROLL",
        "Pudgy Penguins",
    ]
)
```

## Output
- Results are saved to `Traders.csv` in the project root, including:
  - Account Address
  - Token Name
  - Token Amount
  - Total PnL ($)
  - Win Ratio
  - Sharpe Ratio
  - Sortino Ratio
  - Date Range

## Notes
- The script is multi-threaded for speed, but API rate limits may still apply.
- Make sure your `.env` file is present and correct.
- For best results, use exact coin names or symbols as listed by CoinGecko.

## Onwer
Muhammad-Faizan AI ENGINEER