#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import threading
import time
import random
import json
import logging
import re


def find(string):

    # findall() has been used
    # with valid conditions for urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


class ProxyStoreThread(threading.Thread):
    def __init__(self, refresh: int = 30):
        super(ProxyStoreThread, self).__init__()
        self._stop_event = threading.Event()
        self.api = "http://pubproxy.com/api/proxy"
        self.params = {"level": "anonymous", "limit": 5, "type": "http"}

        self.refresh = refresh

        self.proxies = set([])
        self.blacklist = set([])

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def retrieve_proxies(self):
        try:
            response = requests.get(self.api, timeout=5, params=self.params).json()
        except Exception as e:
            print("error retrieving")
        for host in response["data"]:
            ip = host["ipPort"]
            if ip not in self.blacklist:
                self.proxies.add(ip)

    def get(self):
        if len(self.proxies) < 5:
            self.retrieve_proxies()
        proxy = random.randint(0, len(self.proxies) - 1)
        return list(self.proxies)[proxy]

    def drop(self, host):
        self.proxies.remove(host)
        self.blacklist.add(host)

    def run(self):
        while not self.stopped():

            # reset blacklist every 60 seconds
            self.blacklist = set([])

            self.retrieve_proxies()

            time.sleep(self.refresh)
        else:
            print("Terminating ProxyStoreThread for now!!")


class SciHubDownloader:
    def __init__(self, proxy_store, base="https://sci-hub.mksa.top/"):
        self.base = base
        self.proxy_store = proxy_store

    def fetch(
        self,
        doi: str,
        max_attempts: int = 30,
    ):

        proxy = self.proxy_store.get()
        link = None
        for i in range(max_attempts):
            try:
                proxy_dict = {"http": "http://" + proxy}
                target = self.base + doi
                response = requests.get(target)
                response = response.text
            except Exception as e:
                time.sleep(0.5)
                self.proxy_store.drop(proxy)
                proxy = self.proxy_store.get()
                logging.warn(e)
                continue

            start = response.find("<embed type")
            end = response.find("</embed>")
            response = response[start:end]
            urls = find(response)
            if len(urls) == 0:
                break
            link = urls[0]

            pdf_loc = link.find(".pdf")
            link = link[: pdf_loc + 4]
            if not link.startswith("http"):
                link = "https://" + link
            break

        return link

    def download(
        self, pdf: str, export_name: str = "paper.pdf", max_attempts: int = 30
    ):

        downloaded = False
        proxy = self.proxy_store.get()
        for i in range(max_attempts):
            try:
                r = requests.get(pdf, proxies={"http": "http://" + proxy}, stream=True)
            except Exception as e:
                time.sleep(0.1)
                self.proxy_store.drop(proxy)
                proxy = self.proxy_store.get()
                logging.warn(e)
                continue

            with open(export_name, "wb") as fd:
                for chunk in r.iter_content(100):  # number is chunksize
                    fd.write(chunk)

            downloaded = True
            break

        return downloaded


class Scraper:
    def __init__(self, proxy_store: ProxyStoreThread):
        self.proxy_store = proxy_store

    def _proxy_request(self, url, query, proxy):

        proxy_dict = {"http": "http://" + proxy}
        response = requests.get(url, proxies=proxy_dict, timeout=5, params=query)

        return response.json()

    def scrape_paper(self, paper_id: str, max_attempts=100):

        api = "https://api.semanticscholar.org/graph/v1/paper/{}"

        query = {
            "fields": "title,venue,year,abstract,authors,references,fieldsOfStudy,externalIds,referenceCount,citationCount"
        }

        proxy = self.proxy_store.get()

        response = None
        for i in range(max_attempts):
            try:
                response = self._proxy_request(
                    api.format(paper_id),
                    query,
                    proxy,
                )

                # cool down
                time.sleep(0.2)

                break

            except Exception as e:
                self.proxy_store.drop(proxy)
                proxy = self.proxy_store.get()
                print("error", e)

        if response is not None:
            # pretty print
            # print(json.dumps(response, sort_keys=True, indent=2))
            pass

        return response

    def search_by_keyword(self, keywords: [], max_attempts=100):
        api = "https://api.semanticscholar.org/graph/v1/paper/search"
        query = {"query": "+".join(keywords), "fields": "paperId,title,authors"}

        proxy = self.proxy_store.get()

        response = None
        for i in range(max_attempts):
            try:
                response = self._proxy_request(
                    api,
                    query,
                    proxy,
                )

                # cool down
                time.sleep(0.2)

                break

            except Exception as e:
                self.proxy_store.drop(proxy)
                proxy = self.proxy_store.get()
                print("error", e)

        if response is not None:
            # pretty print
            print(json.dumps(response, sort_keys=True, indent=2))
            pass

        return response

    def scrape_author(self, author_id: str, max_attempts=100):

        api = "https://api.semanticscholar.org/graph/v1/author/{}"
        query = {
            "fields": "authorId,paperCount,citationCount,hIndex,name,papers.abstract,papers.title,papers.year,papers.venue,papers.fieldsOfStudy"
        }

        proxy = self.proxy_store.get()

        response = None
        for i in range(max_attempts):
            try:
                response = self._proxy_request(
                    api.format(author_id),
                    query,
                    proxy,
                )

                # cool down
                time.sleep(0.2)

                break

            except Exception as e:
                self.proxy_store.drop(proxy)
                proxy = self.proxy_store.get()
                print("error", e)

        if response is not None:
            # pretty print
            # print(json.dumps(response, sort_keys=True, indent=2))
            pass

        return response
        s = scraper.scrape_paper("de2eb091c0f3219d23c5d249fc1ca6ff272fffd9")
