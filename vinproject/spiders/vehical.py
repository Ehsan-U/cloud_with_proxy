
import scrapy
import json
from datetime import datetime
import sys
from scrapy.spidermiddlewares.httperror import HttpError
import logging
import requests
import asyncio
from proxybroker import Broker
from random import choice

class Myproxies():
    def __init__(self):
        self.proxie = list()
        self.proxies = asyncio.Queue()
        self.broker = Broker(self.proxies)
        
    def setupp(self):
        tasks = asyncio.gather(
        self.broker.find(types=['HTTP', 'HTTPS'], limit=1),
        self.show(self.proxies))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(tasks)

    async def show(self,proxies):
        while True:
            proxy = await proxies.get()
            if proxy is None:
                break
            else:
                await self.send(proxy)
    async def send(self,proxy):
        self.proxie.append(f"{proxy.host}:{proxy.port}")

class VehicalSpider(scrapy.Spider):
    name = 'vehical'
    allowed_domains = ['vehiclehistory.com']
    vin_list = list()
    i =0
    one_time = True
    features = ['Braking Assist','Blind Spot Monitoring','Adaptive Cruise Control','Lane Keep Assist','Lane Departure Warning','Automatic Breaking']
    ######
    # response = requests.get('http://httpbin.org/ip').content
    # dict = json.loads(response)
    # my_ip = dict.get('origin')
    proxy = ''
    def fetch_proxy(self):
        p = Myproxies()
        p.setupp()
        self.proxy = p.proxie[0]
        # return ip only, use for in url
        return self.proxy.split(':')[0]
    ############

    def take_vins(self):
        if self.one_time:
            self.one_time = False
            with open('1000_.json','r') as f:
                self.vin_list = json.load(f)
                return self.take_vins()
        else:
            extract_vin = self.vin_list.pop()
            return extract_vin

    def save_game(self):
        now = datetime.now()
        current = now.strftime("%H:%M:%S").replace(':','')
        with open(f'rem_file.json','w') as file:
            json.dump(self.vin_list,file)
            print('\n\nGame Saved!\n\n')

    def start_requests(self):
        vin = self.take_vins()
        url = 'https://www.vehiclehistory.com/data?operationName=getVinChainReport&variables={"vin":"{v}","ip":"{ip}"}&extensions={"persistedQuery":{"version":1,"sha256Hash":"d465778edd4c81cbddc47b642fe9587b5c47a15195d746b02d0c5930ffcefb5b"}}'.replace('{v}',vin).replace('{ip}',self.fetch_proxy())
        yield scrapy.Request(url,callback=self.custom_parse,errback=self.catch,meta={'proxy':self.proxy,'vin':vin},headers={
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
            try:
                url = 'https://www.vehiclehistory.com/data?operationName=getVinChainReport&variables={"vin":"{v}","ip":"{ip}"}&extensions={"persistedQuery":{"version":1,"sha256Hash":"d465778edd4c81cbddc47b642fe9587b5c47a15195d746b02d0c5930ffcefb5b"}}'.replace('{v}',vin).replace('{ip}',self.fetch_proxy())
                yield scrapy.Request(url,callback=self.parse,errback=self.catch,meta={'proxy':self.proxy,'vin':vin},headers={
                    'accept':'*/*',
                    'content-type':'application/json',
                    'Referer':f'https://www.vehiclehistory.com/vin-report/{vin}',
                    'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                    'sec-ch-ua-mobile':'?0',
                    'sec-ch-ua-platform':'"Windows"',
                })
            except KeyboardInterrupt:
                self.save_game()

    def rotate_ip(self):
        #windscribe.login('bipevo7717', 'bipevo7717@wwdee.com')
        #windscribe.connect(rand=True)
        # checking new ip
        response = requests.get('http://httpbin.org/ip').content
        dict = json.loads(response)
        #self.my_ip = dict.get('origin')


    def catch(self,failure):
        self.save_game()
        if failure.check(HttpError):
            status = failure.value.response.status
            logging.error(f'\nHttpError on {failure.value.response.url} > {status}\n')
            #print('\n[+] Chaning IP\n')
            #self.rotate_ip()
            self.custom_parse(None)

    def parse(self, response):
        if response != None:
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
        else:
            pass  
            
