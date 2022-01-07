import scrapy
import json
from datetime import datetime
import sys

class SecondSpiderSpider(scrapy.Spider):
    name = 'second_spider'
    allowed_domains = ['vehiclehistory.com']
    vin_list = list()
    i =0
    one_time = True
    features = ['Braking Assist','Blind Spot Monitoring','Adaptive Cruise Control','Lane Keep Assist','Lane Departure Warning','Automatic Breaking']


    def take_vins(self):
        if self.one_time:
            self.one_time = False
            with open(r'C:\Users\Ryzen\Documents\vinproject\vinproject\spiders\1000_.json','r') as f:
                self.vin_list = json.load(f)
                return self.take_vins()
        else:
            extract_vin = self.vin_list.pop()
            return extract_vin

    def save_game(self):
        now = datetime.now()
        current = now.strftime("%H:%M:%S").replace(':','')
        with open(f'file{current}.json','w') as file:
            json.dump(self.vin_list,file)
            print('\n\nGame Saved!\n\n')

    def start_requests(self):
        vin = self.take_vins()
        url = 'https://www.vehiclehistory.com/data?operationName=getVinChainReport&variables={"vin":"{v}","ip":"111.119.185.23"}&extensions={"persistedQuery":{"version":1,"sha256Hash":"d465778edd4c81cbddc47b642fe9587b5c47a15195d746b02d0c5930ffcefb5b"}}'.replace('{v}',vin)
        yield scrapy.Request(url,callback=self.custom_parse,errback=self.catch,meta={'vin':vin},headers={
            'accept':'*/*',
            'content-type':'application/json',
            'Referer':f'https://www.vehiclehistory.com/vin-report/{vin}',
            'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile':'?0',
            'sec-ch-ua-platform':'"Windows"',
        })

    def custom_parse(self,response):
        self.parse(response)
        for vin in self.vin_list:
                
            url = 'https://www.vehiclehistory.com/data?operationName=getVinChainReport&variables={"vin":"{v}","ip":"111.119.185.23"}&extensions={"persistedQuery":{"version":1,"sha256Hash":"d465778edd4c81cbddc47b642fe9587b5c47a15195d746b02d0c5930ffcefb5b"}}'.replace('{v}',vin)
            yield scrapy.Request(url,callback=self.parse,errback=self.catch,meta={'vin':vin},headers={
                'accept':'*/*',
                'content-type':'application/json',
                'Referer':f'https://www.vehiclehistory.com/vin-report/{vin}',
                'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                'sec-ch-ua-mobile':'?0',
                'sec-ch-ua-platform':'"Windows"',
            })

    def catch(self,failure):
        print(f'\n{failure.value.response.status}\n')
        #self.save_game()
        

    def parse(self, response):
        data = json.loads(response.body)
        self.i +=1
        vin = response.request.meta.get('vin')
        print(f'\n\n[+]Extracting >> {vin,self.i}\n')
        
        try:
            specs = data['data']['vinChainReport']['specs']
            equipment = data['data']['vinChainReport']['equipment']
            car_dict = dict()
            car_dict['VIN'] = vin
            for item_ in specs:
                car_dict[item_.get('name')] = item_.get('value')
            for feature in self.features:
                car_dict[feature] = 1 if feature in equipment else 0
            yield car_dict
        except TypeError:
            pass
            
            
