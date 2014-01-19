import os
import csv


PATHS = {
	# Paths of model and tagger needed for part of speech tagging
	'POS_MODEL': '../data/english-left3words-distsim.tagger',
	'POS_TAGGER': '../data/stanford-postagger.jar',

	# Paths of output files generated (while doing feature extraction)
	'POS': '../output/output_pos.csv',
	'TRANSACTIONS': '../output/output_transactions.csv',
	'APRIORI': '../output/output_apriori.csv',
	'COMPACT_PRUNING': '../output/output_compact_pruning.csv',
	'REDUNDANCY_PRUNING': '../output/output_redundancy_pruning.csv',

	# Paths of output files generated (while determining opinion orientation)
	'OPINION_WORDS': '../output/output_opinion_words.csv',
	'KNOWN_OPINIONS': '../output/output_known_opinions.csv',

	# Path of initial list of opinion words with orientation
	'ORIGINAL_ADJECTIVES': '../data/original_adjectives.csv'
}


dir = os.path.dirname(__file__)
for key, value in PATHS.items():
	PATHS[key] = os.path.join(dir, value)


def write_csv(path, rows):
	with open(path, 'wb') as f:
		file_writer = csv.writer(f)
		file_writer.writerows(rows)


def read_csv(path):
	content = []
	with open(path, 'rb') as f:
		file_reader = csv.reader(f)
		for row in file_reader:
			content.append(row)

	return content
