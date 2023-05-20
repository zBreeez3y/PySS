# PySS
A script written on Python3 that will query RSS feeds from a list and email you the latest articles that are published. 

## What does PySS do? 
- PySS was created to be ran as a scheduled task that executes at the top of the hour. 
- Upon execution, PySS will run through a list of RSS URL's and query the HTML of the entire feed.
- It then parses the HTML of each feed for the <link> tags as these are the tags that contain the URL to the feed's articles. 
- PySS will then write all the links to a temporary text file, where it will compare against the current list of article URLs from the prior run
  - The first time running, it will only create the original list. Every subsequent run after will write to a temp list and compare with the original. 
- If any differences are found, PySS will create a new list and append each new article URL to the list, and email that list to you using the Gmail SMTP server
#### Note: PySS will create a file called "error.log" in the scripts PWD if any errors occurr

## Setup
- Create an App password for your gmail account you'll use to send the RSS emails (Highly recommended to create a burner Gmail account for this script)
- Create an environment variable called "gmailpass" and set the value to the app password you created
- Edit lines 50 and 51 to provide the address for the sender of the RSS email, and the address for the receiver of the RSS email. 
- Create a scheduled task to run every hour from the time of start, indefinitely (or schedule an end time). 
