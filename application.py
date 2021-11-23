#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import threading
import time
import platform
import random
import subprocess

class ProxyStoreThread(threading.Thread):
    def __init__(self):     
        super(ProxyStoreThread, self).__init__()    
        self._stop_event = threading.Event()   
        self.api = 'http://pubproxy.com/api/proxy'
        self.params = {
            'level': 'anonymous', #anonymous
            'limit': 5,
            'type': 'http'
        }
        
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
            print('error retrieving')
        for host in response['data']:
            ip = host['ipPort']
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
            print('Terminating ProxyStoreThread')
    
class Scraper:
    def __init__(self):
        pass
    
    def proxy_request(self, url, query, proxy):

        response = requests.get(url, proxies={'http': 'http://'+proxy}, timeout=5, params=query)

        return response.json()

if __name__ == "__main__":
    proxyStore = ProxyStoreThread()
    proxyStore.start()
    scraper = Scraper()
    
    for i in range(10):
        proxy = proxyStore.get()
        while True:
            try:
                print(proxy)
                res = scraper.proxy_request("https://api.semanticscholar.org/graph/v1/paper/649def34f8be52c8b66281af98ae884c09aef38b", {'fields': 'authors'}, proxy)
                print(res)
                time.sleep(0.2)
                break
            except Exception as e: 
              proxyStore.drop(proxy)
              proxy = proxyStore.get()
        
    proxyStore.stop()