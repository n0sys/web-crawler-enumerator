import json
from src.classes import Crawl
import src.functions as functions
import time

def start(urls, settings):
    # Define global variables used to store collected data
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
    # Loop breaks when crawling_json['urls_to_visit'] is empty
    try:
        while True:
            with open(".wce/crawling.json") as crawling_file:
                crawling_json = json.load(crawling_file)
            # breaks loop if urls_to_visit list is empty
            if not crawling_json['urls_to_visit']:
                break
            url_to_visit = crawling_json['urls_to_visit'][0].strip()
            #TODO: add js web suppport - if site requires js, wont load with requests library
            print("[+] Visiting url: ", url_to_visit)
            request = Crawl(url_to_visit)
            if request.session.status_code >= 200 and request.session.status_code < 400:
                request.get_urls()
                # get forms if -nf not specified in script arguments | forms added directly to forms.json
                if not settings.no_forms:
                    request.get_forms()
                # get comments if -nc not specified in script arguments | comments added directly to comments.json
                if not settings.no_comments:
                    request.get_comments()
                # get parameters if -np not specified in script arguments | parameters added directly to parameters.json
                if not settings.no_params:
                    request.get_parameters()
            else:
                print("[!] '" + request.url + "' returned status code " + str(request.session.status_code) + " - Not visited")
            # add visited url to history to avoid it being visited again later
            crawling_json['history'].append(url_to_visit)
            # remove visited url from queue
            crawling_json['urls_to_visit'].pop(0)
            # Save changes to crawling_json
            with open('.wce/crawling.json', 'w') as crawling_file:
                json.dump(crawling_json, crawling_file)
            # checks history before adding new urls to visit
            if settings.crawl:
                request.add_new_urls()
            time.sleep(settings.delay)
        # output the results
        functions.output_results(settings)
    except KeyboardInterrupt:
        functions.output_results(settings)
    except Exception as e:
        print("Error:", str(e))
        functions.output_results(settings)