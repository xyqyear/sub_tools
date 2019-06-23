# -*- encoding:utf-8 -*-
import requests

socks5_proxy_ip = '127.0.0.1'
socks5_proxy_port = 1080

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}


def main():
    video_id = input('plz enter the video ID(e.g. RGQe8waGJ4w):')
    proxy_url = f'socks5://{socks5_proxy_ip}:{socks5_proxy_port}'
    proxies = {'http': proxy_url, 'https': proxy_url}
    image_content = requests.get(f'https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg', headers=headers, proxies=proxies).content
    with open('cover.jpg', 'wb') as image_file:
        image_file.write(image_content)


if __name__ == '__main__':
    main()
