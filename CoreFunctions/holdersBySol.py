import requests
import random
import time
from tqdm import tqdm
def SolScan_holders_fetch(address = None,token_price = 0,StartPage=1,EndPage=1,rangeStart=50000, rangeEnd=200000,verbose=False):
    try:
        final_list = []
        if StartPage == 0:
            StartPage+=1
        for i in tqdm(range(StartPage,EndPage),colour="BLUE"):
            sec = random.randint(2,5)
            if verbose:
                print(f"Waiting for {sec} Seconds... (Page {i+1})")
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
                if 'data' in response_json:
                    for holder in response_json['data']:
                        TokenHoldingPrice = (holder['amount']/(10**holder['decimals']))*token_price
                        if   TokenHoldingPrice >= rangeStart and TokenHoldingPrice <=  rangeEnd:
                            if verbose:
                                print(f"Got Account : {holder['owner']}\nToken Amount Holding: {TokenHoldingPrice}")
                            final_list.append(
                                {
                                    'address': holder['address'],
                                    'TokenAmount': TokenHoldingPrice,
                                    'owner': holder['owner'],
                                }
                            )
                        else:
                            if verbose:
                                print(f"Account : {holder['owner']}\nToken Amount Holding: {TokenHoldingPrice}\nCraitera NOT MATCHED")
                else:
                    if verbose:
                        print(f"No 'data' in response for page {i+1}")
            else:
                if verbose:
                    print(f"Failed to fetch page {i+1}: Status code {response.status_code}")
        if not final_list:
            print(f"Got No Results for : {address}")
        return final_list
    except Exception as e:
        print(f"Error : \n{e}")  
