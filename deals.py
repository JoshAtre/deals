import csv
import sys

import pprint as pprint
import requests
import logging
import concurrent.futures

from typing import Dict, List
from urllib.parse import urljoin, urlparse

from html_similarity import similarity
from timeit import default_timer as timer

MAX_DEALS = 200
HTTP_TIMEOUT_SEC = 10
SIMILARITY_THRESHOLD = 0.7
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/83.0.4103.97 Safari/537.36"}


def load_deals(deals_file: str) -> List[Dict[str, str]]:
    with open(deals_file) as f:
        a = [{k: str(v) for k, v in row.items()}
             for row in csv.DictReader(f.readlines()[0:MAX_DEALS + 1], skipinitialspace=True, delimiter="\t")]
    return a


def redirect_link(url: str) -> str:
    newURL = url

    while True:
        response = requests.get(newURL, headers=HEADERS, timeout=HTTP_TIMEOUT_SEC, allow_redirects=False)
        logging.info(response.status_code)
        # print(f"{response.status_code} {url}")
        # Raise an HTTPError for certain status codes
        response.raise_for_status()
        if response.status_code == 301 or response.status_code == 302:
            logging.info(response.headers.get("Location"))
            newURL = response.headers.get("Location")
        else:
            break
    return newURL


def remove_query_string(url: str) -> str:
    return urljoin(url, urlparse(url).path)


def get_body(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=HTTP_TIMEOUT_SEC)
    if response.status_code != 200:
        raise Exception(f"ERROR: Got {response.status_code} for {url}")
    return response.text


def get_similarity(url1: str, url2: str) -> int:
    body1 = get_body(url1)
    body2 = get_body(url2)
    return similarity(body1, body2)


def process_deal(deal: Dict[str, str]) -> None:
    logging.info(f"processing deal: {deal['description']}")
    try:
        new_url = redirect_link(deal["url"])
        new_url = remove_query_string(new_url)
        similarity_score = get_similarity(deal["url"], new_url)
        if similarity_score > SIMILARITY_THRESHOLD:
            out_deals.append({"url_new": new_url, "description": deal["description"], "url": deal["url"]})
        else:
            out_deals.append({"url_new": None, "description": deal["description"], "url": deal["url"]})
    except Exception as e:
        logging.error(e)
        out_deals.append({"url_new": None, "description": deal["description"], "url": deal["url"]})


def process_deals() -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_deal, load_deals("pammcduc_deals.tsv"))


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, format="[%(threadName)s] %(levelname)s - %(message)s", level=logging.INFO)
    pp = pprint.PrettyPrinter(indent=2)
    start_time = timer()
    out_deals: List[Dict[str, str]] = []
    process_deals()
    pp.pprint(out_deals)
    elapsed_time_ms = round(1000*(timer() - start_time))
    logging.info(f"Elapsed time: {elapsed_time_ms} msec")
