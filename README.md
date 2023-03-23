# Web Crawler and Enumerator
## Introduction
WCE is a tool designed to do the first steps of Enumeration in Web Pentesting.

Input the URLs you want to search and the tool will output for you the parameters, urls, comments and forms found on these Web pages. 

You can choose to use the crawl feature as well to ask the script to do web crawling and discover + search other urls found on the pages you input.

## Installation
Just clone the repo (could upload it on pypi later)
```
$ git clone git@github.com:n0sys/web-crawler-enumerator.git
```

Then install dependencies
```
$ pip3 install -r requirements.txt
```

## Usage
### Basic
To search through a single URL just type
```
$ python3 main.py -u URL
```

Searching through a list of URLs also supported. Just add the URLs to a file and run
```
$ python3 main.py -f FILE
```

To enable crawling feature add --crawl argument
```
$ python3 main.py -u URL --crawl
```

### Arguments
The script accepts the following arguments
```
  -h, --help            show this help message and exit
  -u URL, --url URL     Specifies a single URL to scan
  -f FILE, --file FILE  Reads a list of URLs from a text file [each URL on a separate line]
  -c, --crawl           Turns on web crawling, tells the script to enumerate found URLs from same domain
  -np, --no-parameters  No parameters would be output
  -nc, --no-comments    No comments would be output
  -nf, --no-forms       No forms would be output
```

## TODO
- Follow redirects
- Add more info in output for forms
- Output URLs hierarchicaly
- Information gathering from other sources
- Split urls.json between all_urls and new_urls for every iteration of the loop 

---

> Work on this project is still in progress
test
