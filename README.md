# SemanticScholar API Scraper
Scraper for the SemanticScholar API using a pool of public proxies for downloading PDFs from SciHub. **

## Example Usage

```python
import application as app
import logging

# Create & start proxy store (assigns proxies to requests)
proxy_store = app.ProxyStoreThread(30)
proxy_store.start()

# Create scraper for Semantic Scholar API
scraper = app.Scraper(proxy_store)

# reference/key for an interesting paper
seed = "b395775f1bcd80416b93f6380cea999063e0589d"

# Retrieve all references from a paper
res = scraper.scrape_paper(seed)
refs = [ref["paperId"] for ref in res["references"]]
refs = list(filter(lambda r: r is not None, refs))

# Create PDf loader for SciHub
loader = app.SciHubDownloader(proxy_store)

for ref in refs:

    # Scrape meta-data for paper
    res = scraper.scrape_paper(ref)


    # obtain external identifiers (e.g. DOI)
    ids = res["externalIds"]
    
    if "DOI" in ids:

        # Retrieve DOI from scraping result
        doi = ids["DOI"]

        # Generate download link from SciHub
        link = loader.fetch(doi)

        if link is not None:

            # create custom name for downloaded PDF
            title = res["title"].replace(" ", "_")
            year = str(res["year"])
            export_name = year + "_" + title

            # download the acutal PDF
            loader.download(link, export_name=year + "_" + title)

    else:
        logging.debug("No digital object identifier found")
```
