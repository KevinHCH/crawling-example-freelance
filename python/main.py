import httpx
import json
import re
import asyncio
from parsel import Selector as Parser
from urllib.parse import urlparse, urljoin
from pprint import pprint
from cleantext import clean

urls = [
    "https://www.startups.fyi/product",
    "https://www.startups.fyi/product?e52a550f_page=2",
    "https://www.startups.fyi/product?e52a550f_page=3",
]

selectors = {
    "startup_selector": ".interview-card",
    "startup_name_selector": ".name-title::text",
    "startup_revenue_selector": ".person-designation-flex-div div:last-child::text",
    "startup_description_selector": ".card-para::text",
    "startup_link_selector": ".pirsch-event-webclick::attr(href)",
    "details_selector": "#w-node-ff2e0bc1-92d9-b6ad-ddce-4fa56601f5e8-a330d4fe .div-block-58",
}


def get_html_page(url):
    response = httpx.get(url)
    dom = Parser(response.text)
    return dom


async def get_html_page_async(client, url):
    response = await client.get(url)
    dom = Parser(response.text)
    return dom


def get_domain(url):
    domain = urlparse(url)
    return domain.netloc


def make_absolute(domain, path):
    return urljoin(domain, path)


def get_startups(url):
    dom = get_html_page(url)
    startups = dom.css(selectors.get("startup_selector"))
    startup_urls = [make_absolute(url, startup.attrib['href'])
                    for startup in startups]
    return startup_urls


def kebab_case(string):
    return re.sub(r'([a-z])([A-Z])', r'\1-\2', string).lower()


def remove_emojis(text):
    return clean(text, no_emoji=True)


def save(path, data, indent=2):
    print(f"Saving data to: {path}")
    file = open(path, 'w', encoding='utf-8')
    file.write(json.dumps(data, indent=indent))
    file.close()


async def get_startup_details(client, url):
    dom = await get_html_page_async(client, url)
    startup_name = dom.css(selectors.get("startup_name_selector")).get()
    startup_revenue = dom.css(selectors.get("startup_revenue_selector")).get()
    startup_description = dom.css(selectors.get(
        "startup_description_selector")).get()
    startup_link = dom.css(selectors.get("startup_link_selector")).get()
    startup_link = get_domain(startup_link)

    div_blocks = dom.css(selectors.get("details_selector"))
    values = dict()

    for div_block in div_blocks:
        key = div_block.css('.project-tag::text').get()
        key = remove_emojis(key).strip()
        value = div_block.css('div:last-child::text').get()
        values[kebab_case(key)] = value.strip() if value else None
    return {
        "name": startup_name,
        "description": startup_description,
        "revenue": startup_revenue,
        "url": startup_link,
        "data": values,
    }


async def main():
    data = list()
    tasks = list()
    startup_detail_urls = list()
    for url_page in urls:
        startup_urls = get_startups(url_page)
        startup_detail_urls = startup_detail_urls + startup_urls

    async with httpx.AsyncClient() as client:
        total_urls = len(startup_detail_urls)
        for i, url in enumerate(startup_detail_urls):
            print(f"url: {i} of {total_urls} - {url}")
            tasks.append(get_startup_details(client, url))
        data = await asyncio.gather(*tasks)
        save('./startups.json', data)


if __name__ == "__main__":
    asyncio.run(main())
