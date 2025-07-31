import requests
import random
import time
def Helius_holders_fetch(address = None,token_price = 0):
    try:
        # final_list = []
        # for i in range(10):
        #     sec = random.randint(2,5)
        #     print(f"Waiting for {sec} Seconds...")
        #     time.sleep(sec)
            import requests
            import json

            url = "https://mainnet.helius-rpc.com/?api-key=f6de3717-a781-4359-93f4-5d41dc0ca48b"

            payload = json.dumps({
            "jsonrpc": "2.0",
            "id": "1",
            "method": "getProgramAccounts",
            "params": [
                "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                {
                "filters": [
                    {
                    "dataSize": 165
                    },
                    {
                    "memcmp": {
                        "offset": 0,
                        "bytes": "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv"
                    }
                    }
                ],
                "encoding": "jsonParsed",
                'dataSlice.length':1
                }
            ]
            })
            headers = {
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print(response.text)


            # response = requests.request("GET", url, headers=headers, data=payload)
            # if response.status_code == 200:
            #     response_json = response.json()
            #     for holder in response_json['data']:
            #         TokenHoldingPrice = (holder['amount']/(10**holder['decimals']))*token_price
            #         if   TokenHoldingPrice >= 50000 and TokenHoldingPrice <=  200000:
            #             final_list.append
            #             (
            #                     {
            #                         'address': holder['address'],
            #                         'TokenAmount': TokenHoldingPrice,
            #                         'owner': holder['owner'],
            #                     }
            #             )
            #     return final_list
    except Exception as e:
        print(f"Error : \n{e}")  
if __name__ == ("__main__"):
    Helius_holders_fetch()