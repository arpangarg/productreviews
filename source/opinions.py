from nltk.corpus import wordnet as wn
from common import *


class OpinionMining(object):

	def get_opinion_words(self):
		'''
			Determine opinion words from product reviews
		'''
		pos_sentences = read_csv(PATHS['POS'])
		features = read_csv(PATHS['REDUNDANCY_PRUNING'])

		print 'Extracting opinion words...'

		opinion_sentences = []

		for feature in features:
			for pos_sentence in pos_sentences:
				if self.contains_feature(feature[1:], pos_sentence[1:]):
					opinion_words = self.opinion_from_sentence(pos_sentence[1:])
					if opinion_words:
						opinion_sentences.append(
							[' '.join(feature[1:])] + \
							[pos_sentence[0]] + \
							opinion_words
						)

		write_csv(PATHS['OPINION_WORDS'], opinion_sentences)

		print 'Finished extracting opinion words...'


	def contains_feature(self, feature, pos_sentence):
		'''
			Returns true if the product feature is present in the sentence
		'''
		for feature_word in feature:
			in_sentence = False
			for word in pos_sentence:
				if word.split(':')[0].lower() == feature_word:
					in_sentence = True
			if not in_sentence:
				return False
		return True


	def opinion_from_sentence(self, pos_sentence):
		'''
			Returns a list of opinion words from the sentence
		'''
		return [word.split(':')[0].lower() for word in pos_sentence
				if word.split(':')[1] == 'ADJP' or word.split(':')[1] == 'JJ' or
				word.split(':')[1] == 'JJR' or word.split(':')[1] == 'JJS']


	def get_opinion_orientations(self):
		'''
			Uses the WordNet database to determine sentiment orientations of
			all opinion words extracted from the product reviews
		'''
		print 'Determining orientation of opinion words...'

		original_adjectives = read_csv(PATHS['ORIGINAL_ADJECTIVES'])
		opinion_words = read_csv(PATHS['OPINION_WORDS'])

		known_opinions = dict()
		for row in original_adjectives:
			known_opinions[row[0]] = row[1]

		unknown_opinions = list(set([o for r in opinion_words for o in r[2:]]))

		size_before = 0
		size_after = 1

		while size_before != size_after:
			size_before = len(known_opinions)

			for opinion in unknown_opinions:
				orientation = None
				if opinion in known_opinions:
					continue
				synonyms, antonyms = self.get_syn_ant(opinion)
				for syn in synonyms:
					if syn in known_opinions:
						orientation = known_opinions[syn]
				for ant in antonyms:
					if ant in known_opinions:
						orientation = self.opposite_opinion(known_opinions[ant])

				if orientation:
					known_opinions[opinion] = orientation
					unknown_opinions.remove(opinion)
			size_after = len(known_opinions)

		write_csv(PATHS['KNOWN_OPINIONS'], known_opinions.items())

		print 'Finished determining orientation of opinion words'


	def opposite_opinion(self, orientation):
		'''
			Returns the opposite of the given orientation
		'''
		return 'positive' if orientation == 'negative' else 'negative'


	def get_syn_ant(self, adjective):
		'''
			Uses the WordNet database to find synonyms and antonyms of the
			given adjective
		'''
		synonyms = []
		antonyms = []
		synsets = wn.synsets(adjective, pos=wn.ADJ)

		for synset in synsets:
			synonyms.extend(synset.lemma_names)
			antonyms.extend(self.antonyms_from_lemmas(synset.lemmas))

			similar_syns = synset.similar_tos()
			for similar in similar_syns:
				synonyms.extend(similar.lemma_names)
				antonyms.extend(self.antonyms_from_lemmas(similar.lemmas))

			also_sees = synset.also_sees()
			for also_see in also_sees:
				synonyms.extend(also_see.lemma_names)
				antonyms.extend(self.antonyms_from_lemmas(also_see.lemmas))

		return list(set(synonyms)), list(set(antonyms))


	def antonyms_from_lemmas(self, list_lemmas):
		'''
			Returns all antonyms of the given list of lemmas
		'''
		antonyms = []
		for lemma in list_lemmas:
			lemma_ant = lemma.antonyms()
			for each_lemma in lemma_ant:
				antonyms.append(each_lemma.name)
		return antonyms


	def summary_of_results(self):
		'''
			Aggregates the results to associate the pros and cons to
			each product feature
		'''
		print 'Aggregating results...'

		opinions = read_csv(PATHS['OPINION_WORDS'])
		opinion_orientation = read_csv(PATHS['KNOWN_OPINIONS'])

		known_opinions = {}
		for opinion_word in opinion_orientation:
			known_opinions[opinion_word[0]] = opinion_word[1]

		results = {}
		for opinion_sentence in opinions:
			orientation = self.sentence_orientation(
				known_opinions,
				opinion_sentence[2:]
			)
			if orientation == 0:
				continue
			else:
				if opinion_sentence[0] not in results:
					results[opinion_sentence[0]] = [[], []]
				if orientation > 0:
					results[opinion_sentence[0]][0].append(opinion_sentence[1])
				else:
					results[opinion_sentence[0]][1].append(opinion_sentence[1])

		print 'Finished aggregating results...'

		return results


	def sentence_orientation(self, known_opinions, opinion_words):
		'''
			Determines the orientation of a particular sentence given its
			opinion words
		'''
		orientation = 0
		for word in opinion_words:
			if word not in known_opinions:
				continue
			else:
				if known_opinions[word] == 'positive':
					orientation += 1
				else:
					orientation -= 1
		return orientation
