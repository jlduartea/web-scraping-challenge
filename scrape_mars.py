#Dependecies
import pymongo
import requests
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import lxml
import html5lib



# DB Setup
# 

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 


def init_browser():
    # Variables
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)


def scrape():
    browser = init_browser()
    collection.drop()

    # Nasa Mars news
    
    news_url = 'https://mars.nasa.gov/news/'
    browser.visit(news_url)
    news_html = browser.html
    news_soup = bs(news_html, 'html.parser')
    news_title = news_soup.find("div",class_="content_title").text
    news_parag = news_soup.find("div", class_="rollover_description_inner").text  
    
    # JPL Mars Space Images - Featured Image
    jpl_image_url  = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(jpl_image_url )
    jhtml = browser.html
    jpl_soup = bs(jhtml,"html.parser")
    image_url = jpl_soup.find('div',class_='carousel_container').article.footer.a['data-fancybox-href']
    base_link = "https:"+jpl_soup.find('div', class_='jpl_logo').a['href'].rstrip('/')
    feature_image_url = base_link+image_url
    featured_image_title = jpl_soup.find('h1', class_="media_feature_title").text.strip()

    # Mars fact
    facts_url = 'http://space-facts.com/mars/'
    #Read and parse url
    mars_data = pd.read_html(facts_url)
    mars_df = mars_data[0]
    mars_df = mars_df.rename(columns = {0: 'Description', 1: 'Values'})
    mars_df_html= mars_df.to_html(header=False, index=False)


    # Mars Hemispheres
    Hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(Hemisphere_url)     
    Hemisphere_html = browser.html
    mh_soup = bs(Hemisphere_html,"html.parser")
    results = mh_soup.find_all("div",class_='item')
    hemisphere_image_urls = []
    for result in results:
            product_dict = {}
            titles = result.find('h3').text
            end_link = result.find("a")["href"]
            image_link = "https://astrogeology.usgs.gov/" + end_link    
            browser.visit(image_link)
            html = browser.html
            soup= bs(html, "html.parser")
            downloads = soup.find("div", class_="downloads")
            image_url = downloads.find("a")["href"]
            product_dict['title']= titles
            product_dict['image_url']= image_url
            hemisphere_image_urls.append(product_dict)

    # Close the browser after scraping
    browser.quit()

    # Return results
    mars_data ={
		'news_title' : news_title,
		'summary': news_parag,
        'featured_image': feature_image_url,
		'featured_image_title': featured_image_title,
		'fact_table': mars_df_html,
		'hemisphere_image_urls': hemisphere_image_urls,
        'news_url': news_url,
        'jpl_url': jpl_image_url,
        'fact_url': facts_url,
        'hemisphere_url': Hemisphere_url,
        }
    collection.insert(mars_data)
