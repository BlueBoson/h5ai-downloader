import os
import argparse
from urllib.parse import urlparse, unquote
import threading
from concurrent.futures import ThreadPoolExecutor
import time

import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup


args, pr, path_visited, pvl, pool = None, None, None, None, None
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
futures = []


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str, help='URL to h5ai directory (with or without http(s):// both supported)')
    parser.add_argument('-w', '--workers', type=int, default=10, help='Number of workers')
    parser.add_argument('-o', '--output', type=str, default='.', help='Output directory')
    parser.add_argument('--no-dir', dest='no_dir', action='store_true', help='Do not create a seperate directory')
    parser.add_argument('-t', '--test', dest='test', action='store_true', help='Only print files')
    parser.add_argument('-s', '--ssl', dest='ssl', action='store_true', help='Force to use SSL')
    parser.add_argument('--overwrite', dest='overwrite', action='store_true', help='Overwrite existing files')
    parser.add_argument('-b', '--block', type=int, default=1024, help='Block size')
    return parser.parse_args()


def get(path):
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1)))
    s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1)))
    r = s.get(pr._replace(path=path).geturl(), headers=headers)
    return r


def os_path(url_path):
    return os.path.join(args.output, *[unquote(p) for p in url_path.split('/')])


def save_file(path):
    fp = os_path(path)
    if os.path.exists(fp) and not args.overwrite:
        return
    if args.test:
        print(fp)
    else:
        print('Downloading', fp)
        r = get(path)
        with open(fp, 'wb') as f:
            for iter in r.iter_content(args.block):
                f.write(iter)
        print('Downloaded', fp)


def get_item(path):
    dir = os_path(path)
    print('Parsing', pr.netloc + unquote(path))
    os.makedirs(dir, exist_ok=True)
    content = get(path).text
    soup = BeautifulSoup(content, 'html.parser')
    for a in soup.find_all('a'):
        href = a.get('href', '')
        if href.startswith('/') and href.endswith('/'):
            with pvl:
                if href not in path_visited:
                    path_visited.add(href)
                    futures.append([pool.submit(get_item, href), get_item, href])
        elif href.startswith('/'):
            futures.append([pool.submit(save_file, href), save_file, href])
    print('Parsed', pr.netloc + unquote(path))


def main():
    global args, pr, path_visited, pvl, pool, futures
    args = parse_args()
    
    args.url = args.url.rstrip('/') + '/'
    pr = urlparse(args.url)
    if not pr.netloc:
        pr = urlparse('https://' + args.url) if args.ssl else urlparse('http://' + args.url)
    assert pr.scheme and pr.netloc, 'Invalid URL'
    
    if not args.no_dir:
        args.output = os.path.abspath(os.path.join(args.output, unquote(pr.netloc)))
    path_visited = {pr.path}
    pvl = threading.Lock()
    pool = ThreadPoolExecutor(args.workers)
    futures = [[pool.submit(get_item, pr.path), get_item, pr.path]]
    while True:
        failed = [f for f in futures if f[0].exception()]
        if not failed:
            break
        time.sleep(1)
        for f in failed:
            print('Failed', f[1].__name__, f[2], f[0].exception())
            pool.submit(f[1], f[2])
        futures = failed
    pool.shutdown()
    

if __name__ == '__main__':
    main()
