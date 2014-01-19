'''
Usage:
	pipeline.py <url-of-product>
'''

import sys
from source.crawler import Crawler
from source.features import FeatureExtractor
from source.opinions import OpinionMining
from source.display import DisplayResults


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("Incorrect number of arguments!")

	crawler = Crawler(sys.argv[1])

	# crawl the first 100 product reviews from amazon.com
	product_reviews = crawler.get_product_reviews()

	if isinstance(product_reviews, basestring):
		print product_reviews
		sys.exit()

	# Parse reviews into transactions ready to be used for frequent 
	# itemset mining
	FeatureExtractor().get_transactions(product_reviews)

	# Run apriori algorithm to determine the frequent features
	FeatureExtractor().run_apriori()

	# Perform compact pruning and redundancy pruning to disregard features
	# that are likely meaningless
	FeatureExtractor().compact_pruning()
	FeatureExtractor().redundancy_pruning()

	# Find all opinion words from the product reviews
	OpinionMining().get_opinion_words()

	# Determine sentiment orientation of each opinion word
	OpinionMining().get_opinion_orientations()

	# Aggregate results into pros and cons and display them
	results = OpinionMining().summary_of_results()
	DisplayResults(results)
