# Yelp Code to fetch Business details and reviews

## Overview

Script to fetch Yelp business details and reviews for the specified type of business, in the specified location
Read the Yelp-Fusion API documentation for more details about the data
- Search API https://www.yelp.co.uk/developers/documentation/v3/business_search
- Business API https://www.yelp.co.uk/developers/documentation/v3/business
- Reviews API https://www.yelp.co.uk/developers/documentation/v3/business_reviews

## Installation

1. Install a virtual environment of your choice

2. Execute ''' pip install -r requirements.txt '''

3. Edit the config.py with your Cliend Id and Secret
Read here for authentication steps: https://www.yelp.co.uk/developers/documentation/v3/authentication 

4. Edit the run.py with the following details:
   - term(str): Search term (e.g. "food", "restaurants"). If term isn’t included we search everything. The term keyword also accepts business names such as "Starbucks".
   - location(str): Specifies the combination of "address, neighborhood, city, state or zip, optional country" to be used when searching for businesses.
   - records(int): Number of records to be fetched.

5. Execute ''' python run.py '''








