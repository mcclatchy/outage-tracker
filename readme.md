# Requirements

* Python 3
* pip3
* git
* virtualenv/virtualenvwrapper
* AWS S3 bucket configured for with `boto3`
	* instructions for configuration](https://boto3.readthedocs.io/en/latest/guide/configuration.html)

# Instructions

## Get the code

Clone the repo (or clone your own fork)

	git clone git@github.com:mcclatchy/outage-tracker.git

## Set up the environment

Make a virtual environment

	mkvirtualenv outages

Install the requirements

	pip3 install -r requirements.txt

## Test the script

Run the following

	python3 outages.py

After you've confirmed it worked by checking the CLI output and making sure the files are appearing on S3 at the given URLs, you can create a log file. For example:

	touch /home/ubuntu/outage-tracker/outages.py

Then you're ready to set it up on a cron and direct the output to that log file. For example, run every 5 minutes (and depending on your environment, directory locations, etc):

	*/5 * * * * /usr/bin/python3 /home/ubuntu/outage-tracker/outages.py >> /home/ubuntu/outage-tracker/outages.log

Questions? Contact glinch@mcclatchydc.com.

