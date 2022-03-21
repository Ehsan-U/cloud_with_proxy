import asyncio
from http.client import responses
import time
from urllib.parse import urljoin,urlparse
import aiohttp
from asyncio.queues import Queue
from scrapy.selector import Selector
from time import perf_counter

main_url = "lms.ue.edu.pk"
urls = set()
urls_to_scrape = Queue()

async def req(session,url):
    response = await session.get(url)
    if response.status != 200:
        print("None")
    else:
        return response

async def create_tasks(session,urls):
    tasks = []
    for url in urls:
        t = asyncio.create_task(req(session,url))
        tasks.append(t)
    r = await asyncio.gather(*tasks)
    print("Parsing")
    print(len(r))
    await parse(r)

async def parse(responses):
    for r in responses:
        try:
            if r != None:
                body = await r.text()
                selector = Selector(text=body)
                for link in selector.xpath("//a/@href").getall():
                    url = urljoin(str(r.url),link)
                    domain = urlparse(url).netloc
                    if not url in urls and main_url in url:
                        urls.add(url)
                        await urls_to_scrape.put(url)
        except Exception as e:
            print(f"error in parse >> {e}")
            continue

async def new_urls():
    urls = []
    while not urls_to_scrape.empty():        
        url = await urls_to_scrape.get()
        urls.append(url)    
    return urls

async def main():
    urls = ["http://lms.ue.edu.pk/"]
    async with aiohttp.ClientSession() as session:
        print("First time")
        await create_tasks(session,urls)
        while not urls_to_scrape.empty():
            print(f"Recursive {(urls_to_scrape.qsize())}")
            urls = await new_urls()
            #print(f"Recursive {(urls_to_scrape.qsize())}")
            await create_tasks(session,urls)
            if urls_to_scrape.empty():
                print(urls[-1])
                print(f"loop breaks {urls_to_scrape.qsize()}")
                break
            else:
                print(f"loop continue {urls_to_scrape.qsize()}")
                continue

try:
    start = perf_counter()
    asyncio.run(main())
    print(len(urls))
    print(perf_counter()-start)
except Exception as e:
    print(f"Error {e}")