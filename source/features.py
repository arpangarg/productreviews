from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag.stanford import POSTagger
from collections import defaultdict
import re
from common import *


class FeatureExtractor(object):

	def get_transactions(self, product_reviews):
		'''
			Generates a set of transactions ready for frequent itemset mining
			from the crawled product reviews
		'''
		pos_tagger = POSTagger(PATHS['POS_MODEL'], PATHS['POS_TAGGER'])

		pos_output = []
		transactions_output = []

		print 'Generating transactions...'
		product_count = 0
		sentence_count = 0
		for product in product_reviews:
			sentences = sent_tokenize(product)
			for sentence in sentences:
				try:
					sent_pos = pos_tagger.tag(word_tokenize(sentence))
				except UnicodeEncodeError:
					continue
				trans = []
				pos_tags = []
				for word, pos in sent_pos:
					pos_tags.append(':'.join([word, pos]))
					if ((pos == 'NN' or pos == 'NNS' or pos == 'NP') and
						re.match('^[A-Za-z0-9-]+$', word)):
						trans.append(word.lower())
				if trans:
					pos_output.append([sentence] + pos_tags)
					transactions_output.append([sentence] + trans)
					sentence_count += 1
			product_count += 1

			print '---%s Reviews and %s Transactions Parsed---' % (
				product_count,
				sentence_count
			)

		write_csv(PATHS['POS'], pos_output)
		write_csv(PATHS['TRANSACTIONS'], transactions_output)

		print 'Finished generating transactions...'


	def get_min_support_items(self, item_set, transaction_list, item_frequency,
							  min_support):
		'''
			Performs one pass of the apriori algorithm and returns the itemsets
			which have a higher minimum support than min_support
		'''
		local_items = []
		local_frequency = defaultdict(int)

		for item in item_set:
			for transaction in transaction_list:
				in_transaction = True
				for i in item:
					if i not in transaction:
						in_transaction = False
						break
				if in_transaction:
					item_frequency[item] += 1
					local_frequency[item] += 1

		for item, freq in local_frequency.items():
			if (self.item_support(freq, len(transaction_list)) > min_support and
				item not in local_items):
				local_items.append(item)

		return local_items


	def item_support(self, count, num_transactions):
		'''
			Returns the item support based on the itemset's count and total
			number of transactions
		'''
		return count/float(num_transactions)


	def union(self, list_one, list_two):
		'''
			Utility function to combine two lists
		'''
		return list_one + filter(lambda x: x not in list_one, list_two)


	def run_apriori(self):
		'''
			The apriori algorithm used to determine the likely features of the
			product
		'''
		transactions = read_csv(PATHS['TRANSACTIONS'])

		print 'Performing frequent itemset mining...'

		transaction_list = []
		item_set = []

		for row in transactions:
			transaction = row[1:]
			transaction_list.append(transaction)
			for i in transaction:
				if (i,) not in item_set:
					item_set.append((i,))

		item_frequency = defaultdict(int)
		min_support_items = []

		k = 2
		while True:
			item_set = self.get_min_support_items(
				item_set,
				transaction_list,
				item_frequency,
				0.01
			)
			if not item_set:
				break
			min_support_items.extend(item_set)
			item_set = [self.union(i, j) for i in item_set for j in item_set
				if item_set.index(j) > item_set.index(i) and 
				len(self.union(i, j)) == k]
			k += 1

		output_apriori = []

		for item in min_support_items:
			item_sup = self.item_support(
				item_frequency[item],
				len(transaction_list)
			)
			output_apriori.append([item_sup] + list(item))

		write_csv(PATHS['APRIORI'], output_apriori)

		print 'Finished frequent itemset mining...'


	def compact_pruning(self):
		'''
			Performs compact pruning to get rid of feature phrases that are
			likely to be meaningless
		'''
		features = read_csv(PATHS['APRIORI'])
		transactions = read_csv(PATHS['TRANSACTIONS'])

		feature_phrases = [feature for feature in features if len(feature) > 2]
		pruned_features = [feature for feature in features if len(feature) == 2]

		print 'Performing compact pruning...'

		for feature_phrase in feature_phrases:
			count = 0
			for transaction in transactions:
				if set(feature_phrase[1:]).issubset(set(transaction[1:])):
					if self.check_compact(feature_phrase[1:], transaction[0]):
						count += 1
						if count == 2:
							pruned_features.append(feature_phrase)
							break

		write_csv(PATHS['COMPACT_PRUNING'], pruned_features)

		print 'Finished compact pruning...'


	def check_compact(self, feature_phrase, sentence):
		'''
			Determines if a feature phrase is compact in the given sentence
		'''
		words = word_tokenize(sentence.lower())
		try:
			word_positions = [words.index(word) for word in feature_phrase]
		except ValueError:
			return False
		word_positions.sort()

		for i in range(1, len(word_positions)):
			if word_positions[i] - word_positions[i-1] > 2:
				return False
		return True


	def redundancy_pruning(self):
		'''
			Gets rid of single word features which are likely to be a part of
			a feature phrase only
		'''
		print 'Performing redundancy pruning...'

		num_transactions = 0
		with open(PATHS['TRANSACTIONS']) as f:
			for line in f:
				num_transactions += 1

		min_p_support = 3.0/num_transactions

		features = read_csv(PATHS['COMPACT_PRUNING'])

		feature_phrases = [feature for feature in features if len(feature) > 2]
		feature_words = [feature for feature in features if len(feature) == 2]
		pruned_features = []

		for feature_word in feature_words:
			p_support = float(feature_word[0])
			for feature_phrase in feature_phrases:
				if set(feature_word[1:]).issubset(set(feature_phrase[1:])):
					p_support -= float(feature_phrase[0])
			if p_support > min_p_support:
				pruned_features.append(feature_word)

		pruned_features.extend(feature_phrases)

		write_csv(PATHS['REDUNDANCY_PRUNING'], pruned_features)

		print 'Finished redundancy pruning...'
