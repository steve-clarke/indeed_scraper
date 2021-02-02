# Indeed Data Scraper

This webscraper script crawls au.indeed.com for job information based on user input. 

My goal for this project is different from similar projects, because I wanted to process the **job description** data, in the hopes that they will reveal the most common technologies and skills that firms want their employees to be proficient in.

The script does this by identifying the keywords that occur most often in the set of all available job descriptions (ignoring common English words like 'a', 'the' etc). I suspect a pattern of common technologies could emerge as commonly included in job descriptions - for example, AWS, Python, React, C/C++, etc.

I have been careful to save the keywords from each description only once, so as to avoid skewing of data by descriptions that use the same term multiple times.

## Functionality

* Accepts user input for job type and location
* Uses BeautifulSoup and Selenium libraries in Python to extract data from the website's HTML structure
* Collates data including job name, company name, and the description keywords from each listing 
* Analyses the set of all description keywords to determine which keywords appear most often
* Optionally offers data in a spreadsheet format for further processing


## Usage
First, use pip to install the relevant packages on your virtual session:

```
$: pip3 install selenium
$: pip3 install urllib
$: pip3 install bs4
$: pip3 install pandas
$: pip3 install requests
```

Then, in an interactive session, run:
```
>>> import indeed_scraper
>>> indeed_scraper.find_jobs()
```

Then follow the prompts, supplying parameters as required.

The 50 most common keywords across all the job listings will be printed to the console.

Optionally, you can ask for an xlsx file to be output upon completion.

## Future Functionality

The following functionality is yet to be added: 

* Automatic final page selection (currently supports reading multiple pages of job ads, but defaults to crawling first page only)
* Support for multiple OSes and Chrome versions (see _compatibility_ below)

## Compatibility

This script was written on MacOS 11.1, and relies on the user having Chrome version 87.0.4280.xxx for the Selenium crawler to work.

In the future I will build support for all OSes and Chrome versions.

## Author

[Steve Clarke](https://github.com/steve-clarke)
