import requests
def AccountVerification(address):
    system_account = "11111111111111111111111111111111"
    url = f"https://api-v2.solscan.io/v2/account?address={address}&view_as=account"

    payload = {}
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'if-none-match': 'W/"b61-oRLtoj69Z7A9rjLsrjhm+AA6Pk8"',
    'origin': 'https://solscan.io',
    'priority': 'u=1, i',
    'referer': 'https://solscan.io/',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'Cookie': '_ga=GA1.1.509847261.1750787802; _ga_PS3V7B7KV0=GS2.1.s1751133733$o4$g1$t1751139155$j60$l0$h0'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    try:
        if response.status_code == 200:
            response_json = response.json()
            if "metadata" in response_json:
                account_detail = response_json['metadata']['accounts']
                if system_account in account_detail:
                    return True
                else:
                    return False
    except Exception as e:
        print(f"Error In Verifcation Module : {e}")
    # print(response.text)
