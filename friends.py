import streamlit as st
import pandas as pd
import numpy as np
import os
import pysrt
import spacy
import time
import glob2



st.title('Friends word study')

def main():
	files = getfiles()
	selected_episode = select_episode()
	st.write(selected_episode)
	subs, df = loadsubs(selected_episode)
	values = ['PUNCT', 'NUM', 'X', 'SYM']
	
	#drop rows that contain any value in the list
	df = df[df.pos.isin(values) == False]

	select_pos = st.sidebar.multiselect(
     		'Parts of Speech',
     		['SCONJ', 'PRON', 'VERB', 'PUNCT', 'AUX', 'PART', 'NOUN', 			'DET', 'ADJ', 'PROPN', 'ADP', 'ADV', 'CCONJ', 'INTJ', 'NUM', 		'SYM', 'X'],
     		['VERB', 'ADJ','NOUN'])

	
	#words = df[df.word.unique()]
	#st.table(words)
	add_selectbox = st.sidebar.slider('Word mentions', min_value=1, 			max_value=100, value=5, step=1)
	
	for p in select_pos:
		st.write(str(p))
		st.subheader(posdic[str(p)])
		filtered = df[df.pos == str(p)]
		counts = filtered.groupby('pos')['word'].value_counts().reset_index(level=0)
		counts = counts[counts.word >= add_selectbox]
		st.table(counts)
	
	#Search word
	st.header('Search for a word')
	words = df.word.unique()
	
	selectedword = st.selectbox('Search for a word',(df.word.unique()))
	st.write(selectedword)
	if selectedword:
		results = [i for i in subs if selectedword in i.text]
	
		st.write(len(results), ' mentions of ', selectedword, ' found.')
		st.write([r.text for r in results])
	#add audio?
	
	
@st.cache
def getfiles():
	files = glob2.glob("friends/*")
	return files
	
def createdic():
	return dic

def select_episode():
	files=getfiles()
	selected_episode = st.selectbox("Select episode", 				options=files, index=0, key=None, on_change=None)
	return selected_episode

def select_pos():
	selected_pos = st.selectbox("Select part of speech",
		 ('VERB','ADJECTIVE','NOUN'))
	return selected_pos

def loadsubs(selected_episode):
	try:
		subs = pysrt.open(selected_episode, encoding="ISO-8859-1")
	except:
		pass	
	try:
		subs = pysrt.open(selected_episode, encoding="utf-8")
	except:
		pass
	allsubs = [s.text for s in subs]
	corpus = ''.join(allsubs)
	corpus = corpus.replace('\n', '').replace('\u200e', '')
	nlp = spacy.load("en_core_web_sm")
	doc = nlp(corpus)
	pos = [(token.text, token.pos_) for token in doc]
	df = pd.DataFrame(pos, columns = ['word','pos'])
	return subs, df

def analyze():
	return None



def searchword(word='sorry'):
	results = [i for i in subs if word in i.text]
	
	return st.write(len(results), ' mentions of ', word, ' found.')
	
def wordfamily():
	return family


    
posdic = {'VERB': 'verb','ADJ': 'adjective','ADV': 'adverb','AUX': 'auxiliary','CONJ': 'conjunction','CCONJ': 'coordinating conjunction',
'DET': 'determiner','INTJ': 'interjection','NOUN': 'noun','NUM': 'numeral','PART': 'particle',
'PRON': 'pronoun','PROPN': 'proper noun','PUNCT': 'punctuation','SCONJ': 'subordinating conjunction',
'SYM': 'symbol','X': 'other', 'ADP': 'adposition'}

if __name__ == "__main__":
	main()

