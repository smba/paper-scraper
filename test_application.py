#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import application as app



class TestSciHubDownloader(unittest.TestCase):

    def setUp(self):
        self.proxy_store = app.ProxyStoreThread(10)
        self.proxy_store.start()
        
        self.instance = app.SciHubDownloader(self.proxy_store)
        
    def tearDown(self):
        self.proxy_store.stop()
    
    def test_fetch(self):
        doi = '10.1007/s10270-018-0662-9'
        a = self.instance.fetch(doi)
        
    def test_download(self):
        name = 'test_paper.pdf'
        link = 'https://twin.sci-hub.se/6685/d2c9689c55325d981b67dd9cfc47492e/kolesnikov2018.pdf'
        self.instance.download(link, name)
        

if __name__ == '__main__':
    #unittest.main()
    proxy_store = app.ProxyStoreThread(30)
    proxy_store.start()
    
    scraper = app.Scraper(proxy_store)
    
    res = scraper.scrape_paper('b395775f1bcd80416b93f6380cea999063e0589d')
    refs = [ref['paperId'] for ref in res['references']]
    refs = list(filter(lambda r: r is not None, refs))
    
    loader = app.SciHubDownloader(proxy_store)
    
    for ref in refs:
        res = scraper.scrape_paper(ref)
        ids = res['externalIds']
        if 'DOI' in ids:
            doi = ids['DOI']
            link = loader.fetch(doi)
            
            print(link)
            if link is not None:
                title = res['title'].replace(' ', '_')
                year = str(res['year'])
                loader.download(link, export_name=year+'_'+title)
        else:
            print('no doi, but', ids)
            
    proxy_store.stop()
    