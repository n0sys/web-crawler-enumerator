import sys
import argparse
import re
import os
from src.crawl import start
from src.classes import Settings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog= 'wce', 
            description='Web Enum Made Ez', 
            )

    # Script Arguments
    parser.add_argument('-u','--url', help='Specifies a single URL to scan' ) 
    parser.add_argument('-f','--file', type=argparse.FileType('r'), help='Reads a list of URLs from a text file [each URL on a separate line]')
    parser.add_argument('-c', '--crawl', action='store_true', help='Turns on web crawling, tells the script to enumerate found URLs from same domain')
    parser.add_argument('-np', '--no-parameters',action='store_true', help='No parameters would be output')
    parser.add_argument('-nc', '--no-comments',action='store_true', help='No comments would be output')
    parser.add_argument('-nf', '--no-forms',action='store_true', help='No forms would be output')
    parser.add_argument('-d', '--delay', type=float, help='Add delay between requests (To be used with --crawl option)', default=0)
    args = parser.parse_args()
    # Check args
    if args.url is not None and args.file is not None:
        sys.exit('Error: either input a url or a file')
    
    if args.url is None and args.file is None:
        parser.print_help()
        sys.exit()

    urls: list = []
    if args.url is None:
        urls = args.file.readlines()
    else:
        urls = [args.url]
    
    for url in urls:
        if re.match('https?\:\/\/[^.]',url) is None:
            sys.exit('URLs must be in format http(s)://xxxx')

    # check if delay is used without crawl
    if args.delay != 0 and not args.crawl:
        sys.exit('Error: Delay must only be used with crawl option (--crawl)')

    # Creating the settings dict to be passed to the loop
    settings = Settings(args.crawl, args.no_parameters, args.no_comments, args.no_forms, args.delay)
    
    # Initiate local storage directory
    if '.wce' not in os.listdir():
        os.mkdir('.wce')
    # Initialize clean json files
    with open(".wce/parameters.json","w") as pf:
        pf.write("{}")
    with open(".wce/comments.json","w") as cmf:
        cmf.write("{}")
    with open(".wce/urls.json","w") as uf:
        uf.write("{}")
    with open(".wce/forms.json","w") as ff:
        ff.write("{}")
    with open(".wce/crawling.json","w") as crf:
        crf.write("{}")
   
    start(urls, settings)