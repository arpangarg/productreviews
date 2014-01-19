from requests import get
from lxml import etree


class Crawler(object):

	def __init__(self, original_url):
		self.OriginalUrl = original_url
		self.ReviewsUrl = 'http://www.amazon.com/product-reviews/{0}'

	def get_product_reviews(self):
		'''
			Returns 100 of the most helpful reviews from Amazon.com
		'''
		response = get(self.OriginalUrl)
		if response.status_code != 200:
			return 'Incorrect URL or unable to connect to the server'

		num_reviews = self.number_of_reviews(response)

		if num_reviews < 100:
			return ''.join([
				'Only ',
				str(num_reviews),
				' reviews found. Atleast 100 reviews required'
			])

		print 'Crawling reviews...'

		doc = etree.HTML(response.content)
		prod_asin = doc.xpath(
			'//form[@id="addToCart"]/input[@id="ASIN"]/@value'
		)[0]

		self.ReviewsUrl = self.ReviewsUrl.format(prod_asin)

		product_reviews = []

		for page in range(1, 11):
			product_reviews += self.reviews_from_page(page)

		print 'Finished crawling...'

		return product_reviews

	def number_of_reviews(self, response):
		'''
			Returns the number of reviews present for a product
		'''
		doc = etree.HTML(response.content)
		num_reviews = doc.xpath('//div[contains(@id, "average")]/a/text()')[0]

		return int(num_reviews.split()[0])

	def reviews_from_page(self, page):
		'''
			Returns the 10 reviews on that page (Amazon yields 10 reviews 
			per page)
		'''
		review_page = get(self.ReviewsUrl, params={'pageNumber': page})
		doc = etree.HTML(review_page.content)

		reviews = doc.xpath('//div[contains(@style, "margin-left")]/text()')

		single_review = ''
		total_reviews = []
		for each_part in reviews:
			part = each_part.strip()
			if part:
				single_review += part + ' '
			else:
				total_reviews.append(single_review)
				single_review = ''

		return filter(None, total_reviews)
