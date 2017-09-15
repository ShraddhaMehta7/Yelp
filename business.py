import json
import csv
import urllib
import requests
import os 
from config import Config
from urllib.parse import quote
from urllib.parse import urlencode

class YelpBusiness:
    """Yelp request object"""
    def __init__(self,config):
        """
        config: object containing client_id, secret and grant_type
        """
        self.client_id = config.CLIENT_ID
        self.client_secret = config.CLIENT_SECRET
        self.grant_type = config.GRANT_TYPE
        self.api_host = config.API_HOST
        self.search_path = config.SEARCH_PATH
        self.business_path = config.BUSINESS_PATH
        self.token_path = config.TOKEN_PATH
    
    def obtain_bearer_token(self, host, path):
        """Given a bearer token, send a GET request to the API.
        Args:
            host (str): The domain host of the API.
            path (str): The path of the API after the domain.
        Returns:
            str: OAuth bearer token, obtained using client_id and client_secret.
        """
        url = '{0}{1}'.format(host, quote(path.encode('utf8')))
        data = urlencode({
        'client_id': self.client_id,
        'client_secret': self.client_secret,
        'grant_type': self.grant_type,
        })
        headers = {
        'content-type': 'application/x-www-form-urlencoded',
        }
        response = requests.request('POST', url, data=data, headers=headers)
        bearer_token = response.json()['access_token']
        return bearer_token 
    
    def request(self, host, path, bearer_token, url_params=None):
        """Given a bearer token, send a GET request to the API.
        Args:
            host (str): The domain host of the API.
            path (str): The path of the API after the domain.
            bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
            url_params (dict): An optional set of query parameters in the request.

        Returns:
            dict: The JSON response from the request.

        Raises:
            HTTPError: An error occurs from the HTTP request.
        """
        url_params = url_params or {}
        url = '{0}{1}'.format(host, quote(path.encode('utf8')))
        headers = {
            'Authorization': 'Bearer %s' % bearer_token,
        }
        response = requests.request('GET', url, headers=headers, params=url_params)
        return response.json()
    
    def get_search_results(self,bearer_token,term,location,limit, offset):
        """Query the Search API by a search term and location.

        Args:
            term (str): The search term passed to the API.
            location (str): The search location passed to the API.

        Returns:
            dict: The JSON response from the request.
        """
        url_params = {
            'term': term,
            'location': location,
            'limit': limit,
            'offset': offset
        }
        return self.request(self.api_host, self.search_path, bearer_token, url_params=url_params)
    
    def get_business_details(self, bearer_token, business_id):
        """Query the Business API by a business ID.

        Args:
            business_id (str): The ID of the business to query.

        Returns:
            dict: The JSON response from the request.
        """
        business_path_full = self.business_path + business_id
        return self.request(self.api_host, business_path_full, bearer_token) 
    
    def get_reviews(self, bearer_token, business_id):
        """Query the Reviews API by a business ID.
        
        Args:
            business_id(str): The ID of the business to query.
            
        Returns:
            dict: The JSON response from the request.
        """
        reviews_path = self.business_path + business_id + '/reviews'
        return self.request(self.api_host, reviews_path, bearer_token)
    
    def get_all_business_details(self,csvfilep,term,location,records):
        """Gets details of up to 1000 businesses from the Search endpoint Search endpoint and passes the business IDs to the Business endpoint to fetch reviews. Writes results to a CSV file.
        https://www.yelp.co.uk/developers/documentation/v3/business
        Args:
            csvfilp(str): The file pointer to the CSV where the data is to be written
            term (str): The search term passed to the API.
            location (str): The search location passed to the API
            records(int): The number of records to be written to the file
             
        Returns:
            writes to a CSV file containing relevant business details       
               
        Note:
            Yelp Search endpoint returns up to 1000 businesses based on the provided search criteria
            Max results in one call is 50, set using 'search_limit'. Next set of results can be obtained using 'offset'
        """
        bearer_token = self.obtain_bearer_token(self.api_host, self.token_path)
        response = self.get_search_results(bearer_token, term, location, 1, 0)
        businesses = response.get('businesses')
        total_no_businesses = response.get('total')
        
        if records > 1000:
            records = 1000
            search_limit = 50
        elif records <= 50:
            search_limit = records
        elif records > 50 and records <= 1000:
            search_limit = 50
            
        offset = 0
        flag = True

        while offset < min(records, total_no_businesses): 
            response = self.get_search_results(bearer_token, term, location, search_limit, offset) 
            businesses = response.get('businesses')
            j = 0
            while j < search_limit:
                business_id = businesses[j]['id']

                try:
                    business_details = self.get_business_details(bearer_token, business_id)
                except Exception as e:
                    print("Error ouccured in fetching reviews for business id " + business_id)
                    print("Error: " + str(e))
                    j=j+1
                    continue

                name = business_details.get('name',"")
                is_claimed = business_details.get('is_claimed',"")
                is_closed = business_details.get('is_closed',"")
                url = business_details.get('url',"")
                price = business_details.get('price',"")
                rating = business_details.get('rating',"")
                review_count = business_details.get('review_count',"")
                phone = business_details.get('phone',"")
                photos = str(business_details.get('photos',"")).replace(',', ';')            
                hours = business_details.get('hours', "")
                if hours != "":
                    hours_type = hours[0].get('hours_type',"")
                    is_open_now = hours[0].get('is_open_now',"")
                else:
                    hour_type = ""
                    is_open_now = ""                        
                categories = business_details.get('categories',"")
                category_alias = ""
                category_title = ""
                if categories != "":
                    for category in categories:
                        category_alias = category_alias + str(category.get('alias',"")) + "; "
                        category_title = category_title + str(category.get('alias',"")) + "; "
                    category_alias.strip(';')
                    category_title.strip(';')                            
                coordinates = business_details.get('coordinates',"")
                if coordinates != "":
                    latitude = coordinates.get('latitude',"")
                    longitude = coordinates.get('longitude',"")
                else:
                    latitude = ""
                    longitude = ""           
                location = business_details.get('location')
                if location != None:
                    address = str(location.get('address1',"")) + " " + str(location.get('address2',""))+ " " + str(location.get('address3',""))
                    city = location.get('city',"")
                    state = location.get('state',"")
                    zip_code = location.get('zip_code',"")
                    country = location.get('country',"")
                    cross_streets = location.get('cross_streets',"")
                else:
                    address = ""
                    city = ""
                    state = ""
                    zip_code = ""
                    country = ""
                    cross_streets = ""
                            
                transactions = (str(business_details.get('transactions',""))).replace(',',';') 

                business_dict = {"id" : business_id, "name" : name, "is_claimed" : is_claimed, "is_closed" : is_closed, "url" : url, "price" : price, "rating" : rating, "review_count" : review_count, "phone" : phone, "photos" : photos, "hours_type" : hours_type, "is_open_now" : is_open_now, "category_alias" : category_alias, "category_title" : category_title, "latitude" : latitude, "longitude" : longitude, "address" : address, "city" : city, "state" : state, "zip_code" : zip_code, "country": country, "cross_streets" : cross_streets, "transactions" : transactions}
                
                business_writer = csv.DictWriter(csvfilep, delimiter = '|', fieldnames = business_dict.keys())
                if flag == True:
                    business_writer.writeheader()
                    flag = False
                business_writer.writerow(business_dict)
            
                j = j + 1
                if offset + j > total_no_businesses:
                    break
            offset = search_limit + offset
        

    def get_all_business_reviews(self, csvfilep, term, location, records):
        """Gets details of up to 1000 businesses from Search endpoint and passes the business IDs to the Reviews endpoint to fetch reviews. Writes results to a CSV file.
        https://www.yelp.co.uk/developers/documentation/v3/business_reviews
        Args:
            csvfilp(str): The file pointer to the CSV where the data is to be written
            term (str): The search term passed to the API.
            location (str): The search location passed to the API
            records(int): The number of records to be written to the file
             
        Returns:
            writes to a CSV file containing relevant business details       
               
        Note:
            Yelp Search endpoint returns up to 1000 businesses based on the provided search criteria
            Max results in one call is 50, set using 'search_limit'. Next set of results can be obtained using 'offset'
        """
        bearer_token = self.obtain_bearer_token(self.api_host, self.token_path)
        response = self.get_search_results(bearer_token, term, location, 1, 0)
        businesses = response.get('businesses')
        total_no_businesses = response.get('total')

        if records > 1000:
            records = 1000
            search_limit = 50
        elif records <= 50:
            search_limit = records
        elif records > 50 and records <= 1000:
            search_limit = 50
            
        offset = 0
        flag = True
   
        while offset < min(records,total_no_businesses): 
            response = self.get_search_results(bearer_token, term, location, search_limit, offset) 
            businesses = response.get('businesses')
            j = 0
            while j < search_limit:
                business_id = businesses[j]['id']
                try:
                    business_details = self.get_business_details(bearer_token, business_id)
                except Exception as e:
                    print("Error ouccured in fetching business details for business id " + business_id)
                    print("Error: " + str(e))
                    j=j+1
                    break
                business_name = business_details.get('name',"")
                business_url = business_details.get('url',"")


                try:
                    business_reviews = self.get_reviews(bearer_token, business_id)
                except Exception as e:
                    print("Error ouccured in fetching reviews for business id " + business_id)
                    print("Error: " + str(e))
                    j=j+1
                    break

                total_reviews = business_reviews.get('total',"")
                review_list = business_reviews.get('reviews',"")
                review_text = []
                review_url = []
                review_rating = []
                review_time_created = []
                for review in review_list:
                    review_text.append(review.get('text',""))
                    review_url.append(review.get('url',""))
                    review_time_created.append(review.get('time_created',""))
                    review_rating.append(review.get('rating',""))
                
                review_text_str = str(review_text).replace(',',';')
                review_url_str = str(review_url).replace(',',';')
                review_time_created_str = str(review_time_created).replace(',',';')
                review_rating_str = str(review_rating).replace(',',';')

                review_dict = {"id" : business_id, "business_name" : business_name, "business_url" : business_url, "total_reviews" : total_reviews, "review_text" : review_text_str, "review_url" : review_url_str, "review_rating" : review_rating_str, "review_time_created" : review_time_created_str}            
                review_writer = csv.DictWriter(csvfilep, delimiter='|', fieldnames = review_dict.keys())
                if flag == True:
                    review_writer.writeheader()
                    flag = False
                review_writer.writerow(review_dict)
                
                j = j + 1
                if offset + j > total_no_businesses:
                    break
            offset = search_limit + offset
    
