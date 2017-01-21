#!/usr/bin/env python3
# Author: Sathyan Murugan 
# Year: 2017

'''
This script uses Requests and BeautifulSoup to scrape the 
current bids from all auctions on the Auction site Catawiki
'''


from bs4 import BeautifulSoup
import requests
import datetime
import pandas as pd

#Request data from the auctions site
print('Getting links to all the auctions ending today....')
url = 'https://auction.catawiki.com/'
r  = requests.get(url)

#Parse HTML
html = r.text
soup = BeautifulSoup(html,'html.parser')

#Find the section with current day's auctions
today = datetime.date.today()
ends_today = soup.find_all("section", id="cw-link-{0}".format(today.strftime('%Y-%m-%d')))

#Get a unique list of the links to the auctions
ends_today_links_raw = [link.get('href') for link in ends_today[0].find_all('a')]
ends_today_links = list(set(ends_today_links_raw))

#Loop through each link and get all the bids for all auctions
print('Looping through links and getting the current bids....')
all_auctions_bids = []
counter = 0
for link in ends_today_links:
	counter+=1
	print('scraping auction {0} of {1}'.format(counter,len(ends_today_links)))

	#Get Auction name from URL
	auction_name = link.split('.com/')[1].split('/')[0]

	#Get soup
	r  = requests.get(link)
	html = r.text
	soup = BeautifulSoup(html,'html.parser')

	#Find the bids,clean, separate into sublists
	bids_html = soup.find_all('div',class_='amount')
	bids_text = [bid.text.strip().split('\n') for bid in bids_html]

	#Loop through each bid
	clean_bids = []
	for bid_text in bids_text:

		#Extract only digits
		clean_bid = [''.join(c for c in bid if c.isdigit()) for bid in bid_text]

		#Add the auction name to each sublist
		clean_bid.insert(0,auction_name)
		clean_bids.append(clean_bid)

	all_auctions_bids.append(clean_bids)

#Flatten the list and make it into a dataframe
flat_list_bids = [item for sublist in all_auctions_bids for item in sublist]
df = pd.DataFrame(flat_list_bids,columns = ['Auction','USD','EUR','GBP'])

#Convert strings to integers 
int_cols = ['USD','EUR','GBP']
for col in int_cols:
	df[col] = df[col].apply(lambda row: int(row))

#Print stats
print('Average prices by auction ....\n')
print(df.groupby(df['Auction']).mean())

#Store data as CSV
print('Dumping CSV..')
df.to_csv('scraped_data.csv',index=False)