from business import YelpBusiness
from config import Config

#Instantiate an EPLRequest
Yelp = YelpBusiness(Config)

#Search Query Args
term = 'restaurants'
location = 'New York City, NY'
records = 3 #should be under 1000
business_details_csv = 'business.csv'
business_reviews_csv = 'reviews.csv'

#Write Business details to csv
with open(business_details_csv, "w+", newline="\n", encoding="utf-8") as business_f:
    Yelp.get_all_business_details(business_f, term, location, records)

#Write Business reviews to csv    
with open(business_reviews_csv, "w+", newline="\n", encoding="utf-8") as reviews_f:
    Yelp.get_all_business_reviews(reviews_f, term, location, records)
