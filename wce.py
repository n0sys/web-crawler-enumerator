import sys
import argparse
from crawl import start


if __name__ == "__main__":
    print("""Web Crawler and Enumerator""")
    parser = argparse.ArgumentParser(prog= 'wce', 
            description='Web Enum Made Ez', 
            )

    # Script Arguments
    parser.add_argument('-u','--url', help='Specifies a single URL to scan' ) 
    parser.add_argument('-f','--file', type=argparse.FileType('r'), help='Reads a list of URLs from a text file [each URL on a separate line]')
    parser.add_argument('-c', '--crawl', action='store_true', help='Turns on web crawling, tells the script to enumerate found URLs from same domain')
    parser.add_argument('-np', '--no-parameters',action='store_true', help='No parameters would be output')
    parser.add_argument('-nc', '--no-comments',action='store_true', help='No comments would be output')
    parser.add_argument('-nu', '--no-urls',action='store_true', help='No URLs would be output')
    parser.add_argument('-ni', '--no-inputs',action='store_true', help='No hidden inputs would be output')
    args = parser.parse_args()

    if args.url != None and args.file != None:
        sys.exit('Either input a url or a file')
    
    #TODO: make settings as dict
    settings: dict = {'crawl':args.crawl,
        'no-params':args.no_parameters,
        'no-comments':args.no_comments,
        'no-urls': args.no_urls,
        'no-inputs': args.no_inputs}
    urls: list = []
    if args.url == None:
        urls = args.file.readlines()
    else:
        urls = [args.url]
    start(urls, settings)