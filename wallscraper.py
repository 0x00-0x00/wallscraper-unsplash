#!/usr/bin/env python3.6
#coding:utf-8
import requests
import re
import asyncio
import aiohttp
import tqdm
import string
import random
import sys

def get_download_links(data):
    pattern = "http?s:\/\/[\w]+(?:(?:\.[\w_-]+)+)\/photos\/[a-zA-Z0-9\-]+\/download".encode()
    m = re.findall(pattern, data)
    return m


def format_link_for_download(link):
    return link.replace(b"api.", b"") + b"?force=true"


def request_page_data(link):
    req = requests.get(link)
    return req.text.encode()


def write_to_file(filename, content):
    with open(filename, "wb") as f:
        f.write(content)
    return 0


@asyncio.coroutine
def get(url, conn):
    response = yield from aiohttp.request('GET', url,  connector=conn)
    return (yield from response.read())


@asyncio.coroutine
def download_file(url, connector):
    #  Use the semaphore
    with (yield from r_semaphore):
        content = yield from asyncio.async(get(url, connector))
    length = 12
    random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
    filename = "{0}.jpg".format(random_string)
    write_to_file(filename, content)
    return 0


@asyncio.coroutine
def progressbar(coros):
    for f in tqdm.tqdm(asyncio.as_completed(coros), total=len(coros)):
        yield from f


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {0} <UNSPLASH COLLECTION URL>".format(sys.argv[0]))
        sys.exit(0)

    main_page_data = request_page_data(sys.argv[1])
    download_links = [format_link_for_download(x) for x in get_download_links(main_page_data)]

    #  Maximum of 10 simultaneous downloads
    r_semaphore = asyncio.Semaphore(10)
    connector = aiohttp.TCPConnector(verify_ssl=False)
    coroutines = [download_file(url.decode(), connector) for url in download_links]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(progressbar(coroutines))
