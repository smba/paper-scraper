#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import threading
import time
import random
import json


class ProxyStoreThread(threading.Thread):
    def __init__(self):
        super(ProxyStoreThread, self).__init__()
        self._stop_event = threading.Event()
        self.api = "http://pubproxy.com/api/proxy"
        self.params = {"level": "anonymous", "limit": 5, "type": "http"}

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
            time.sleep(60)
        else:
            print("Terminating ProxyStoreThread for now!!")


class Scraper:
    def __init__(self, proxy_store: ProxyStoreThread):
        self.proxy_store = proxy_store

    def _proxy_request(self, url, query, proxy):

        proxy_dict = {"http": "http://" + proxy}
        response = requests.get(url, proxies=proxy_dict, timeout=5, params=query)

        return response.json()

    def scrape_paper(self, paper_id: str, max_attempts=100):

        api = "https://api.semanticscholar.org/graph/v1/paper/{}"

        query = {"fields": "title,venue,year,abstract,authors,references,fieldsOfStudy,externalIds,referenceCount,citationCount"}

        proxy = self.proxy_store.get()

        response = None
        for i in range(max_attempts):
            try:
                response = scraper._proxy_request(
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
            print(json.dumps(response, sort_keys=True, indent=2))
            pass

        return response
    
    def search_by_keyword(self, keywords: [], max_attempts=100):
        api = "https://api.semanticscholar.org/graph/v1/paper/search"
        query = {
            'query': '+'.join(keywords),
            'fields': 'paperId,title,authors'
        }
    
        proxy = self.proxy_store.get()

        response = None
        for i in range(max_attempts):
            try:
                response = scraper._proxy_request(
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
            'fields': 'authorId,paperCount,citationCount,hIndex,name,papers.abstract,papers.title,papers.year,papers.venue,papers.fieldsOfStudy'
        }
        
        proxy = self.proxy_store.get()

        response = None
        for i in range(max_attempts):
            try:
                response = scraper._proxy_request(
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
            #print(json.dumps(response, sort_keys=True, indent=2))
            pass

        return response
        

if __name__ == "__main__":
    proxyStore = ProxyStoreThread()
    proxyStore.start()
    scraper = Scraper(proxyStore)

    # scrape stuff    

    proxyStore.stop()
