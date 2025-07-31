import requests
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