import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time

def get_brands(url):
    """
    Lấy danh sách các thương hiệu từ URL chính.
    """
    lst_brand_hasaki = []
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        links = soup.find_all('a', href=True)
        hrefs = [link['href'] for link in links if link['href'].startswith("/thuong-hieu")]
        hrefs = set(hrefs)

        for href in hrefs:
            lst_brand_hasaki.append(f"https://hasaki.vn{href}")
    else:
        print(f"Không thể truy cập trang web. Status code: {response.status_code}")
    
    return lst_brand_hasaki


def extract_information_product(product_url):
    """
    Lấy thông tin sản phẩm từ URL của một trang thương hiệu.
    """
    lst_info_product = []
    response = requests.get(product_url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        items = soup.find_all("div", class_="ProductGridItem__itemOuter")

        for item in items:
            dict_info_product = {
                "new_price": item.find("strong", class_="item_giamoi txt_16").text.strip() if item.find("strong", class_="item_giamoi txt_16") else None,
                "old_price": item.find("span", class_="item_giacu txt_12 right").text.strip() if item.find("span", class_="item_giacu txt_12 right") else None,
                "discount": item.find("span", class_="discount_percent2_deal").text.strip() if item.find("span", class_="discount_percent2_deal") else None,
                "sold": item.find("span", class_="item_count_by").text.strip() if item.find("span", class_="item_count_by") else None,
                "vn_name": item.find("div", class_="vn_names").text.strip() if item.find("div", class_="vn_names") else None,
                "en_name": item.find("div", class_="en_names").text.strip() if item.find("div", class_="en_names") else None,
                "url_thumbnail": item.find("img", class_="img_thumb lazy")["data-src"] if item.find("img", class_="img_thumb lazy") and item.find("img", class_="img_thumb lazy").get("data-src") else None
            }

            lst_info_product.append(dict_info_product)
    else:
        print(f"Không thể truy cập sản phẩm từ {product_url}. Status code: {response.status_code}")

    return lst_info_product


def crawl_all_products(lst_brands, delay=1):
    """
    Thu thập thông tin sản phẩm từ danh sách các thương hiệu.
    """
    all_products = []
    for brand in tqdm(lst_brands[:10], desc="Duyệt qua các thương hiệu"):
        lst_product = extract_information_product(brand)
        all_products.extend(lst_product)
        print(f"Đã lấy thông tin sản phẩm từ {brand}")
        time.sleep(delay)
    
    return all_products
