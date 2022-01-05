import json

def take_vins():
    with open('file_thousand.json','r') as f:
        vin_list = json.load(f)
        vin_list = list(filter(None,vin_list))
        extract_vin = vin_list.pop()
        return extract_vin
print(take_vins())