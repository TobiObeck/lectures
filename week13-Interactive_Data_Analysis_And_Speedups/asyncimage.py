import asyncio
import os
from time import time
from id import client_id

import aiohttp

from download import setup_download_dir, get_links

async def async_download_link(session, directory, link):
    """
    Async version of the download_link method we've been using in the other examples.
    :param session: aiohttp ClientSession
    :param directory: directory to save downloads
    :param link: the url of the link to download
    :return:
    """
    download_path = directory / os.path.basename(link)
    async with session.get(link) as response:
        with download_path.open('wb') as f:
            while True:
                # await pauses execution until the 1024 (or less) bytes are read from the stream
                chunk = await response.content.read(1024)
                if not chunk:
                    # We are done reading the file, break out of the while loop
                    break
                f.write(chunk)


# Main is now a coroutine
async def main():
    download_dir = setup_download_dir()
    # We use a session to take advantage of tcp keep-alive
    # Set a 3 second read and connect timeout. Default is 5 minutes
    async with aiohttp.ClientSession(conn_timeout=3, read_timeout=3) as session:
        tasks = [(async_download_link(session, download_dir, l)) for l in get_links(client_id)]
        # gather aggregates all the tasks and schedules them in the event loop
        await asyncio.gather(*tasks, return_exceptions=True)


ts = time()
# Create the asyncio event loop
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    # Shutdown the loop even if there is an exception
    loop.close()
print('Took',time() - ts,'seconds to complete')