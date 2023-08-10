# Bubble Report
A python project to create reports showing the activity of a list of Instagram influencers associated to the Bubbleroom brand.  
By default it will create a report for the month of January 2021, but using the command line options detailed below it can be used to generate a report for any time period.

# Installation
## Prerequisites
Python3 should be installed and accessible on the PATH.  
The steps below assume that the PATH variable `python` points to python 3. If not change the commands accordingly.
## Install Steps
1. `git clone HERE` - clone the repo
2. `cd HERE` - change working directory into the repo
3. `python -m venv .venv` - create a virtual environment called .venv
4. `source .venv/bin/activate` - activate the virtual environment
5. `pip install -r requirements.txt` - install requirements  
6. For Generating PDF (not required unless you want pdf generation)  
    Follow the steps to install wkhtmltopdf [here](https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf)

# Usage
## Prerequisites
The python virtual environment configured earlier is active.
## Basic Usage
`python bubble_report.py [flags]` - general call signature  
`python bubble_report.py --create_pdf=True` - e.g. enable pdf generation  
`python bubble_report.py -s "2021-02-01T12:00:00" -e "2021-04-01T12:00:00"` - e.g. custom start and end dates  
## Command Line Options
| Option | Flag | Description | Default |
| --- | --- | --- | --- |
| help | `-h` or `--help` | display command line documentation| `N/A` |
| create_pdf | `--create_pdf=True` or `--create_pdf=False` | generate a pdf output file | `False` |
| create_html | `--create_html=True` or `--create_html=False` | generate an html output file | `True` |
| start_date | `-s "date"` or `--start_date="date"` | set start date, accepts strings in ISO 8601 format | `2021-01-01T00:00:00` |
| end_date | `-e "date` or `--end_date="date"` | set end date, accepts strings in ISO 8601 format | `2021-01-31T23:59:59` |
| user_csv | `-u "file_path"` or `--user_csv="file_path"` | set file path for user csv, path is relative to current working directory | `users.csv` |
| user_posts_csv | `-p "file_path` or `--user_posts_csv="file_path"` | set file path for user posts csv, path is relative to current working directory | `user_posts.csv` |

# Improvements
These are improvements I would still like to make. The first I expect to complete before final submission as long as I get confirmation of the calculation logic. The second set I will leave as an example of what I would do given more time.
1. Improvements to the calculation logic. It is clear that the numbers in my report differ from the example in a few ways. I have asked for clarification for the calculations that are unclear to me, and when I recieve that clarification I will implement the fixes.
2. Design issues with the generated html/pdf:
    1. The html version doesn't render as individual pages, so the headers and footers for each section only show once.  
    Using the current template as a base and making a Jinja template solely for html output could allow for html specific improvements.
    2. The wkhtmltopdf version does render as individual pages, but I haven't yet implemented the headers and footers as seperate HTML elements to be passed in, and so they also don't appear on every page. Furthermore, since the css isn't aware of the page layout the footers don't extend down to the bottom of the page.  
    Again, using Jinja to tweak the output solely for pdf could allow for pdf specific improvements.  
    [This stackoverflow shows an example how I could implement a dynamic header which knows the page number and can disable itself if needs be, for example on the cover page.](https://stackoverflow.com/questions/11948158/wkhtmltopdf-how-to-disable-header-on-the-first-page)
    3. wkhtmltopdf doesn't support flex boxes, and therefore the layout of elements differs between the two versions in a few places. Thankfully they both look decent, but it is still frustrating that they aren't equivalent.