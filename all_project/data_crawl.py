import aiohttp
import asyncio
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def fetch(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            raise Exception(f"Failed to fetch {url} with status {response.status}")
        return await response.text()


async def extract_brand_urls(base_url):

    async with aiohttp.ClientSession() as session:
        html_content = await fetch(session, base_url)
        soup = BeautifulSoup(html_content, "html.parser")
        links = soup.find_all('a', href=True)

        # Lst URL brand
        brand_urls = [
            f"https://hasaki.vn{link['href']}"
            for link in links
            if link['href'].startswith("/thuong-hieu")
        ]
        return list(set(brand_urls))  # Loại bỏ trùng lặp


async def extract_product_info(session, brand_url):

    products = []
    html_content = await fetch(session, brand_url)
    soup = BeautifulSoup(html_content, "html.parser")

    items = soup.find_all("div", class_="ProductGridItem__itemOuter")
    for item in items:
        product = {
            "new_price": item.find("strong", class_="item_giamoi txt_16").text.strip() if item.find("strong", class_="item_giamoi txt_16") else None,
            "old_price": item.find("span", class_="item_giacu txt_12 right").text.strip() if item.find("span", class_="item_giacu txt_12 right") else None,
            "discount": item.find("span", class_="discount_percent2_deal").text.strip() if item.find("span", class_="discount_percent2_deal") else None,
            "sold": item.find("span", class_="item_count_by").text.strip() if item.find("span", class_="item_count_by") else None,
            "vn_name": item.find("div", class_="vn_names").text.strip() if item.find("div", class_="vn_names") else None,
            "en_name": item.find("div", class_="en_names").text.strip() if item.find("div", class_="en_names") else None,
            "url_thumbnail": item.find("img", class_="img_thumb lazy")["data-src"] if item.find("img", class_="img_thumb lazy") and item.find("img", class_="img_thumb lazy").get("data-src") else None,
        }
        products.append(product)
    return products


async def crawl_brands(base_url):
    async with aiohttp.ClientSession() as session:
        # lst url brand
        brand_urls = await extract_brand_urls(base_url)
        print(f"Found {len(brand_urls)} brands to crawl.")

        # Crawl brand
        all_products = []
        tasks = [extract_product_info(session, url) for url in brand_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle result
        for result in results:
            if isinstance(result, list):
                all_products.extend(result)
            else:
                print(f"Error while crawling: {result}")

        print(f"Total products crawled: {len(all_products)}")
        return all_products
