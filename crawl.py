import json
from classes import Crawl
from functions import get_domains_from_urls, output_results

def start(urls, settings): 
    # Define global variables used to store collected data
    # TODO: check local storage for use instead of global vars
    crawling_json = {}
    crawling_json['urls_to_visit'] = urls
    crawling_json['history'] = []
    crawling_json['domains'] = []
    with open('.wce/crawling.json', 'w') as crawling_file:
        json.dump(crawling_json, crawling_file)
    # Get the domains from user's input and store them in crawling_json['domains']
    get_domains_from_urls(urls)
    # TODO: issue in output urls (found when visiting http://localhost/dashboard)
    # Loop breaks when theres no urls_to_visit in crawling_json
    while True:
        with open(".wce/crawling.json") as crawling_file:
            crawling_json = json.load(crawling_file)
        # breaks loop if urls_to_visit list is empty
        if not crawling_json['urls_to_visit']:
            break
        url_to_visit = crawling_json['urls_to_visit'][0].strip()
        print(url_to_visit)
        #TODO: add js web suppport - if site requires js, wont load with requests library
        #TODO: check response status code
        request = Crawl(url_to_visit,
            settings['no-forms']
            )
        # What to do based on user's request
        if not settings['no-comments']:
            request.get_comments()
        request.get_urls()
        # adds parameters to parameters.json
        if not settings['no-params']:
            request.get_parameters()
        crawling_json['history'].append(url_to_visit)
        crawling_json['urls_to_visit'].pop(0)
        with open('.wce/crawling.json', 'w') as crawling_file:
            json.dump(crawling_json, crawling_file)
        # loads crawling.json and checks history before adding new urls to visit
        if settings['crawl']:
            request.add_new_urls()
        # Add delay?
        # time.sleep(settings['sleep'])
    output_results(settings)