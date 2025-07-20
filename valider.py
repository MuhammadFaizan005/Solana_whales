import requests
def verify_solana_address(address):
    url = f"https://api-v2.solscan.io/v2/search?keyword={address}"

    payload = {}
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'origin': 'https://solscan.io',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://solscan.io/',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json()
    
    return len(response_json.get('data', [])) > 0

if __name__ == "__main__":
    print(verify_solana_address("DBmae92YTQKLsNzXcPscxiwPqMcz9stQr2prB5ZCAHPd"))
