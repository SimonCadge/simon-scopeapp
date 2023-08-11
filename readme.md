# Bubble Report
A python project to create reports showing the activity of a list of Instagram influencers associated to the Bubbleroom brand.  
By default it will create a report for the month of January 2021, but using the command line options detailed below it can be used to generate a report for any time period.

# Installation
## Prerequisites
[Python3](https://www.python.org/downloads/) should be installed and accessible on the PATH.  
* The steps below assume that the PATH variable `python` points to python 3. If not, change the commands accordingly.  

[Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) should also be installed and accessible on the PATH.
## Install Steps
1. Clone the repo  
    `git clone https://github.com/SimonCadge/simon-scopeapp.git`
2. Change working directory to the cloned directory  
    `cd simon-scopeapp`
3. Create a virtual environment called .venv  
    `python -m venv .venv`
4. Activate the virtual environment  
    `source .venv/bin/activate`
5. Install requirements  
    `pip install -r requirements.txt`
6. For Generating PDF (not required unless you want pdf generation)  
    Follow the steps to install wkhtmltopdf [here](https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf)

# Usage
## Prerequisites
The python virtual environment configured earlier is active.  
wkhtmltopdf is installed if pdf generation is desired.
The script should only be called from the root folder of the project. It looks for required files and generates output files relative to the current working directory, so if you call it from somewhere else you'll get strange behaviour.
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

# Technologies
The script is written in Python, and since I have relatively little Python experience I have used quite a standard object-oriented approach.  
The main libraries used are [pydantic](https://docs.pydantic.dev/latest/) for data validation and type checking, and [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) for HTML templating. [pdfkit](https://pypi.org/project/pdfkit/) is used for interacting with wkhtmltopdf, but only if the user requests a pdf output file.  
I expect someone better versed in Python might have used Pandas for parts of the loading, validating and processing of the data. I also considered parallelising parts of the program execution. However, I am a strong believer in avoiding premature-optimisation, especially in a scenario such as a coding interview where time is precious and readability is key, so I implemented the simple, readable and easily maintainable solution first and it performs perfectly well.  
Choosing to use Jinja to render a HTML page and then convert it to a pdf using wkhtmltopdf was the decision that I think has the most downsides. If I were to do this challenge again I would still make the same decision, but I would be very interested to hear suggestions on other approaches I could have taken that might have been smoother. I tried using [pylatex](https://jeltef.github.io/PyLaTeX/current/) initially but very quickly reached a point where half of the code was idiomatic pylatex instructions and the other half were unescaped raw LaTeX instructions, plus I'm not nearly as comfortable with LaTeX as I am with HTML, and using HTML allowed for the choice between an HTML or PDF output, so I switched after about 30 minutes. HTML templating and layouts are very common and have massive adoption, so I figured that choosing that approach would mean there is plenty of support online for any issues I encounter, future maintainers of the code would be more likely to be familiar with the technology, and non-technical users would be a little more likely to understand. That being said, the main downside to HTML and web technologies are the wide varieties in implementation of the HTML spec across different engines, and I came afoul of that here with wkhtmltopdf using a version of QtWebKit that doesn't support modern flex boxes properly. It might be possible to try other web engines to generate the PDF, for example [this python project](https://pypi.org/project/pyhtml2pdf/) makes use of the chromium engine instead, but wkhtmltopdf was clearly the standard online for this approach.

# Improvements
These are improvements I would still like to make. The first I had hoped to complete before final submission. The second set I will leave as an example of what I would do given more time.
1. Improvements to the calculation logic. It is clear that the numbers in my report differ from the example in a few ways.  
When I realised that my numbers differed and that I didn't have a clear enough description of the desired calculations to fix them on my own I reached out to Sebastian at the email he originally contacted me with, stating my best understanding of what the calculations might be, and asking for clarification in a few areas I was sure were incorrect. Unfortunately I didn't hear back from him before submitting this project, so the numbers in the reports generated by this script align with the understanding of the calculations that I stated in that email and not whatever they ideally would be.  
The only field that I don't at least have some idea what it might mean is `photo_tags`. I have looked through the Instagram API documentation and found [a deprecated feature](https://developers.facebook.com/docs/graph-api/reference/v17.0/photo/tags) that lists the users tagged in a photo, but the feature is deprecated and that data doesn't exist in the provided csv file anyway.
2. Design issues with the generated html/pdf:
    1. The html version doesn't render as individual pages, so the headers and footers for each section only show once.  
    Using the current template as a base and making a Jinja template solely for html output could allow for html specific improvements.
    2. The wkhtmltopdf version does render as individual pages, but I haven't yet implemented the headers and footers as seperate HTML elements to be passed in, and so they also don't appear on every page. Furthermore, since the css isn't aware of the page layout the footers don't extend down to the bottom of the page.  
    Again, using Jinja to tweak the output solely for pdf could allow for pdf specific improvements.  
    [This stackoverflow shows an example how I could implement a dynamic header which knows the page number and can disable itself if needs be, for example on the cover page.](https://stackoverflow.com/questions/11948158/wkhtmltopdf-how-to-disable-header-on-the-first-page)
    3. wkhtmltopdf doesn't support flex boxes, and therefore the layout of elements differs between the two versions in a few places. Thankfully they both look decent, but it is still frustrating that they aren't equivalent.
    4. Perhaps other HTML to PDF tools might have a more up to date implementation. The chrome based library linked above will use the version of chrome already installed on the users' machine, and so theoretically would not suffer any inconsistencies with the HTML file. Chrome does also support the custom header and footer html, so I would certainly at least experiment with this going forward.