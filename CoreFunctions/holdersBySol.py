import requests
import random
import time
def SolScan_holders_fetch(address = None,token_price = 0):
    try:
        final_list = []
        for i in range(10):
            sec = random.randint(2,5)
            print(f"Waiting for {sec} Seconds...")
            time.sleep(sec)
            url = f"https://api-v2.solscan.io/v2/token/holders?address={address}&page_size=40&page={i+1}"
            payload = {}
            headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://solscan.io',
            'priority': 'u=1, i',
            'referer': 'https://solscan.io/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Cookie': 'cf_clearance=_gyBWrpv7mpifYDX7ELpTdU_5.ry74R9nnxUbJ9bgi8-1739993738-1.2.1.1-qrkygam73f_JfMEMwLVjHw4EdEGAI_0jzzJ5vi1QhUi9_46PYQKUQx35iz8FXzXfimLSy2WT8n1.dlJEAgMuD2W_yKeaGFCkOHSLvzEeFWSd123BRiDhNq764pcEeCNZsAn7l7cqZ18hpcmorxS2jvyp3ttL0pHEJIOZxE_oZKsJFd8xl7ofQrvErII9EiB5H5ks6MdaTlll3Ty37mfJiCnNhuVHCDeW0Jmjf6899kSf8R2L.RQBHF8bRc9i.NeSxUhQt7I2dUUitIQTZJekphydECoGE8gKBFNsRaDp_nA; _ga=GA1.1.299561973.1753039008; _ga_PS3V7B7KV0=GS2.1.s1753041096$o2$g1$t1753041142$j14$l0$h0'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                response_json = response.json()
                for holder in response_json['data']:
                    TokenHoldingPrice = (holder['amount']/(10**holder['decimals']))*token_price
                    if   TokenHoldingPrice >= 50000 and TokenHoldingPrice <=  200000:
                        final_list.append
                        (
                                {
                                    'address': holder['address'],
                                    'TokenAmount': TokenHoldingPrice,
                                    'owner': holder['owner'],
                                }
                        )
                return final_list
    except Exception as e:
        print(f"Error : \n{e}")  
