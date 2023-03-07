import sys
import argparse
import re
import os
from crawl import start

if __name__ == "__main__":
    #print("""Web Crawler and Enumerator""")
    parser = argparse.ArgumentParser(prog= 'wce', 
            description='Web Enum Made Ez', 
            )

    # Script Arguments
    parser.add_argument('-u','--url', help='Specifies a single URL to scan' ) 
    parser.add_argument('-f','--file', type=argparse.FileType('r'), help='Reads a list of URLs from a text file [each URL on a separate line]')
    parser.add_argument('-c', '--crawl', action='store_true', help='Turns on web crawling, tells the script to enumerate found URLs from same domain')
    parser.add_argument('-np', '--no-parameters',action='store_true', help='No parameters would be output')
    parser.add_argument('-nc', '--no-comments',action='store_true', help='No comments would be output')
    #parser.add_argument('-nu', '--no-urls',action='store_true', help='No URLs would be output')
    parser.add_argument('-nf', '--no-forms',action='store_true', help='No forms would be output')
    args = parser.parse_args()

    if args.url != None and args.file != None:
        sys.exit('Error: either input a url or a file')
    
    if args.url == None and args.file == None:
        parser.print_help()
        sys.exit()
        
    settings: dict = {'crawl':args.crawl,
        'no-params':args.no_parameters,
        'no-comments':args.no_comments,
        #'no-urls': args.no_urls,
        'no-forms': args.no_forms
        }
    urls: list = []
    if args.url == None:
        urls = args.file.readlines()
    else:
        urls = [args.url]
    
    # TODO: find better way to test for URL errors
    for url in urls:
        if re.match('https?\:\/\/[^.]',url) == None:
            sys.exit('URLs must be in format http(s)://xxxx')
    
    # Initiate local storage directory
    if '.wce' not in os.listdir():
        os.mkdir('.wce')
    # Initiate clean parameters.json file 
    with open(".wce/parameters.json","w") as parameters_file:
        parameters_file.write("")
    with open(".wce/comments.json","w") as comments_file:
        comments_file.write("")
    with open(".wce/urls.json","w") as urls_file:
        urls_file.write("")
    with open(".wce/forms.json","w") as forms_file:
        forms_file.write("")
    with open(".wce/crawling.json","w") as crawling_file:
        crawling_file.write("")
    start(urls, settings)