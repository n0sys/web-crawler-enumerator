import json
from classes import Crawl
import functions

def start(urls, settings): 
    # Define global variables used to store collected data
    # TODO: check local storage for use instead of global vars
    crawling_json = {}
    crawling_json['urls_to_visit'] = urls
    crawling_json['history'] = []
    crawling_json['domains'] = []

    # Get the domains from user's input and store them in crawling_json['domains']
    domains_list = functions.get_domains_from_urls(urls)
    for domain in domains_list:
        if domain not in crawling_json['domains']:
            crawling_json['domains'].append(domain)
    with open('.wce/crawling.json', 'w') as crawling_file:
        json.dump(crawling_json, crawling_file)

    # TODO: issue in output urls (found when visiting http://localhost/dashboard)
    # Loop breaks when crawling_json['urls_to_visit'] is empty
    while True:
        with open(".wce/crawling.json") as crawling_file:
            crawling_json = json.load(crawling_file)
        # breaks loop if urls_to_visit list is empty
        if not crawling_json['urls_to_visit']:
            break
        url_to_visit = crawling_json['urls_to_visit'][0].strip()
        #TODO: add js web suppport - if site requires js, wont load with requests library
        #TODO: check response status code
        request = Crawl(url_to_visit,
            settings['no-forms']
            )
        print("Visiting url: "+url_to_visit)
        request.get_urls()
        # get comments -nc not specified in run arguments | comments added directly to comments.json
        if not settings['no-comments']:
            request.get_comments()
        # get parameters -nc not specified in run arguments | parameters added directly to parameters.json
        if not settings['no-params']:
            request.get_parameters()
        # add visited url to history to avoid it being visited again later
        crawling_json['history'].append(url_to_visit)
        # remove visited url from queue
        crawling_json['urls_to_visit'].pop(0)
        # Save changes to crawling_json
        with open('.wce/crawling.json', 'w') as crawling_file:
            json.dump(crawling_json, crawling_file)
        # checks history before adding new urls to visit
        if settings['crawl']:
            request.add_new_urls()
    # output the results
    functions.output_results(settings)