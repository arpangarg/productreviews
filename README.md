# Product Reviews Summary

The purpose of this project is to scrape product reviews from [Amazon.com](http://www.amazon.com/), analyze these reviews using natural language processing techniques, and summarize the product's main features into a list of pros and cons. See pipeline.py for a quick demo.


## Implementation

The techniques proposed by Hu and Liu (see references) are used to implement the system. A brief overview of the **pipeline** is given:

1. **Crawl Reviews**: This is the data collection step, and customer reviews are crawled for the selected product.
2. **Product Features Extraction**: Extract the important product features, such as price or battery life.
	- A) Generate Transactions: This phase consists of two steps,
		* Part of speech tagging is performed on each sentence of each customer review using the Stanford POS Tagger.
		* Nouns and noun phrases are extracted and a set of transactions are formed - ready to be fed for frequent itemset mining.
	- B) Apriori Algorithm: Determine the most common nouns from the set of transactions formed earlier to generate an initial list of product features.
	- C) Prune Features: Perform compact and redundancy pruning as described by Hu and Liu.
3. **Determine Sentiments/Opinions**:
	- A) Extract all the opinion words (in most cases adjectives) from customer reviews.
	- B) Determine the orientation (positive/negative) of the extracted opinion words. This is done by starting with a seed list of known opinions and using the WordNet database to further grow this list.
4. **Present Results**: Aggregate the results into a pros and cons list for each product feature and present the summary using the Tkinter GUI.


## References

Minqing Hu , Bing Liu, Mining and summarizing customer reviews, Proceedings of the tenth ACM SIGKDD international conference on Knowledge discovery and data mining, August 22-25, 2004, Seattle, WA, USA
