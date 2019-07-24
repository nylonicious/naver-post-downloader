import asyncio
import os
import re
import time
from json import loads as loadjson
from sys import version_info
from urllib.parse import unquote, urlparse

import aiohttp


class NaverDownloader:
    def __init__(self, url):
        self.session = None
        asyncio.run(self.queue_downloads(url))

    async def queue_downloads(self, url):
        tasks = []
        title = urlparse(url).query.split('volumeNo=')[1].split('&')[0]
        desiredpath = os.getcwd() + '\\' + title + '\\'
        if not os.path.exists(desiredpath):
            os.makedirs(desiredpath)
        timeout = aiohttp.ClientTimeout(total=30)
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"}
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as self.session:
            async with self.session.get(url) as response:
                text = await response.text()
                for i in text.split("data-linkdata=\'")[1:]:
                    linkdata = loadjson(i.split("\'>\n")[0])
                    if 'src' in linkdata:
                        picture_url = linkdata['src']
                        picture_id = unquote(urlparse(picture_url).path.split('/')[-1])
                        picture_name = re.sub('[<>:\"/|?*]', ' ', picture_id).strip()
                        picture_path = desiredpath + picture_name
                        if not os.path.isfile(picture_path):
                            tasks.append(asyncio.create_task(self.download(picture_url, picture_path)))
                    else:
                        print(f"Error string does not include 'src' {linkdata}")
                await asyncio.gather(*tasks)

    async def download(self, picture_url, picture_path):
        async with self.session.get(picture_url) as r:
            if r.status == 200:
                with open(picture_path, 'wb') as f:
                    print(f'Downloading {picture_url}')
                    f.write(await r.read())
            else:
                print(f'Error {r.status} while getting request for {picture_url}')


def main():
    urlinput = input('Enter post URL: ')
    x = time.time()
    NaverDownloader(urlinput)
    print('Time to complete script: ', time.time() - x)
    input('Press Enter to continue . . . ')


if __name__ == '__main__':
    assert version_info >= (3, 7), 'Script requires Python 3.7+.'
    main()
