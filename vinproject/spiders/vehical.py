from typing import TYPE_CHECKING
import scrapy
import json
import sys

from scrapy.utils.python import garbage_collect

class VehicalSpider(scrapy.Spider):
    name = 'vehical'
    allowed_domains = ['vehiclehistory.com']
    vin_list = list()
    i =1
    one_time = True
    features = ['Braking Assist','Blind Spot Monitoring','Adaptive Cruise Control','Lane Keep Assist','Lane Departure Warning','Automatic Breaking']

    def clean_data(self,vins):
        filtered = list(filter(None,vins))
        gb = "UNKNOWN"
        if gb in filtered:
            ind = filtered.index(gb)
            #print(f'\n\n{ind}\n\n')
            print(f'\n\n{filtered[ind]}\n\n')
            del filtered[ind]
            print(f'\n\n{filtered[ind]}\n\n')
            return filtered


    def take_vins(self):
        if self.one_time:
            self.one_time = False
            with open('/home/zorin/vinproject/vinproject/file_thousand.json','r') as f:
                vins = json.load(f)
                self.vin_list = self.clean_data(vins)
                return self.take_vins()
                
        else:
            extract_vin = self.vin_list.pop()
            return extract_vin


    def start_requests(self):
        
        self.vin = self.take_vins()
        url = 'https://www.vehiclehistory.com/data?operationName=getVinChainReport&variables={"vin":"{vin}","ip":"111.119.187.16"}&extensions={"persistedQuery":{"version":1,"sha256Hash":"d465778edd4c81cbddc47b642fe9587b5c47a15195d746b02d0c5930ffcefb5b"}}'.replace('{vin}',self.vin)
        yield scrapy.Request(url,callback=self.parse,errback=self.catch,headers={
            'accept':'*/*',
            'content-type':'application/json',
            'Referer':f'https://www.vehiclehistory.com/vin-report/{self.vin}',
            'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile':'?0',
            'sec-ch-ua-platform':'"Windows"',
        })


    def handle_err(self):
        self.i+=1
        print(f'\n\n[+]Extracting (handle_err)>> {self.i}\n')
        self.vin = self.take_vins()
        url = 'https://www.vehiclehistory.com/data?operationName=getVinChainReport&variables={"vin":"{vin}","ip":"111.119.187.16"}&extensions={"persistedQuery":{"version":1,"sha256Hash":"d465778edd4c81cbddc47b642fe9587b5c47a15195d746b02d0c5930ffcefb5b"}}'.replace('{vin}',self.vin)
        yield scrapy.Request(url,callback=self.parse,errback=self.catch,headers={
            'accept':'*/*',
            'content-type':'application/json',
            'Referer':f'https://www.vehiclehistory.com/vin-report/{self.vin}',
            'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile':'?0',
            'sec-ch-ua-platform':'"Windows"',
        })

    def parse(self, response):

        #print('\n',response.request.headers.get('User-Agent'),'\n')
        #print('\n',response.url,response.status,'\n')
        data = json.loads(response.body)
        try:
            specs = data['data']['vinChainReport']['specs']
            equipment = data['data']['vinChainReport']['equipment']

            car_dict = dict()
            car_dict['VIN'] = self.vin
        
        
            for item_ in specs:
                car_dict[item_.get('name')] = item_.get('value')
        #yield car_dict

            for feature in self.features:
                car_dict[feature] = 1 if feature in equipment else 0
            yield car_dict
            self.i+=1
            print(f'\n\n[+]Extracting >> {self.vin,self.i}\n')
            
            self.vin = self.take_vins()
            url = 'https://www.vehiclehistory.com/data?operationName=getVinChainReport&variables={"vin":"{vin}","ip":"111.119.187.16"}&extensions={"persistedQuery":{"version":1,"sha256Hash":"d465778edd4c81cbddc47b642fe9587b5c47a15195d746b02d0c5930ffcefb5b"}}'.replace('{vin}',self.vin)
            yield scrapy.Request(url,callback=self.parse,errback=self.catch,headers={
                'accept':'*/*',
                'content-type':'application/json',
                'Referer':f'https://www.vehiclehistory.com/vin-report/{self.vin}',
                'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                'sec-ch-ua-mobile':'?0',
                'sec-ch-ua-platform':'"Windows"',
            })
        except Exception as e:
            # skiping the current vin
            print(f'\nerror >> {self.vin,e}\n')
            self.handle_err()

    def catch(self,failure):
        self.i+=1
        print(f'\n\n[+]Extracting (catch)>> {self.vin,self.i}\n')
        self.vin = self.take_vins()
        url = 'https://www.vehiclehistory.com/data?operationName=getVinChainReport&variables={"vin":"{vin}","ip":"111.119.187.16"}&extensions={"persistedQuery":{"version":1,"sha256Hash":"d465778edd4c81cbddc47b642fe9587b5c47a15195d746b02d0c5930ffcefb5b"}}'.replace('{vin}',self.vin)
        yield scrapy.Request(url,callback=self.parse,errback=self.catch,headers={
            'accept':'*/*',
            'content-type':'application/json',
            'Referer':f'https://www.vehiclehistory.com/vin-report/{self.vin}',
            'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile':'?0',
            'sec-ch-ua-platform':'"Windows"',
        })

