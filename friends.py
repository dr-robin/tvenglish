import streamlit as st
import pandas as pd
import numpy as np
import os
import pysrt
import spacy
import time
import glob2
import re
import matplotlib.pyplot as plt
import chardet

st.title('Friends word study')

def main(df):
	
	
	
	values = ['PUNCT', 'NUM', 'X', 'SYM']
	
	#drop rows that contain any value in the list
	df = df[df.pos.isin(values) == False]
	df = df.groupby('pos')['word'].value_counts().reset_index(level=0)
	df['base_word'] = df.index
	df = df.reset_index(drop=True)
	df = df.rename({'word':'mentions'}, axis=1)
		
	select_pos = st.sidebar.multiselect(
     		'Parts of Speech',
     		['SCONJ', 'PRON', 'VERB', 'PUNCT', 'AUX', 'PART', 'NOUN','DET', 'ADJ', 'PROPN', 'ADP', 'ADV', 			'CCONJ','INTJ', 'NUM','SYM', 'X'],
     		['VERB', 'ADJ','NOUN'])
	select_level = st.sidebar.multiselect(
     	'English Level',
     	['A1', 'A2', 'B1', 'B2', 'C1', 'C2'],
     	['A1','A2'])
     		
	st.header('Words in episode')
	metric1 = df.base_word.unique()
	ncol = len(select_pos)
	col1, col2, col3 = st.columns(3)
	col1 = st.metric('Total', df.base_word.nunique(),)
	col2 = st.metric('Verbs', df[df.pos == 'VERB'].base_word.nunique(),)
	col3 = st.metric('Adjectives', df[df.pos == 'ADJ'].base_word.nunique(),)
	
	add_selectbox = st.sidebar.slider('Word mentions', min_value=1,max_value=100, value=5, step=1)
	
	df_level = pd.read_csv("cambridge_britisheng.csv")
	df_level = df_level.sort_values(by='level',ascending=True)
	df_level = df_level.drop_duplicates(subset=['base_word'], keep='first')
	df_level = df_level[['base_word','level']]
	
	
	df = pd.merge(df_level, df, on='base_word', how='right')
	
	#plotpie(df)
	plotbar(df)
	
	try:
		plotbar(df)
	except Exception as e:
		st.write(e)
		
	try:
		plotpie(df)
	except:
		pass
		
	for p in select_pos:
		st.subheader(posdic[str(p)])
		filtered = df[df.pos == str(p)]
		
		#Show table
		filtered = filtered[filtered.mentions >= add_selectbox]
		st.table(filtered)
	
	#Search word
	st.header('Search for a word')
	words = df.base_word.unique()
	words = np.sort(words)
	#
	selectedword = st.selectbox('Search for a word',words)

	if selectedword:
		results = [i for i in subs if selectedword in i.text]
	
		st.write(len(results), ' mentions of ', selectedword, ' found.')
		st.write([r.text for r in results])
	#add audio?

def getfiles():
	files = glob2.glob("friends/*")
	#files = files.sort()
	return files
	
def createdic():
	return dic

def filesdic(files):
	keys = [f.split('/')[-1].split('.')[0] for f in files]
	d = {k:v for k,v in zip(keys,files)}
	return d
	
def select_episode():
	files = getfiles()
	#make dic
	d = filesdic(files)
	options = list(d.keys())
	selected_episode = st.sidebar.selectbox("Select episode", options=options, index=0, key=None, on_change=None)
	#get filename for selected episode from dic
	selected_episode = d[selected_episode]
	return selected_episode

def select_pos():
	selected_pos = st.selectbox("Select part of speech",
		 ('VERB','ADJECTIVE','NOUN'))
	return selected_pos
	
def getencoding(selected_episode):
	tmp = open(selected_episode, "rb")
	rawdata = tmp.read()
	encode = chardet.detect(rawdata)
	tmp.close()
	encode = encode['encoding']
	return encode
def loadsubs(selected_episode):
	file = open(selected_episode, "rb")
	enc = chardet.detect(file.read())
	enc = enc['encoding']
	st.write(enc)
	file.close()
	subs = pysrt.open(selected_episode,encoding=enc)
	return subs
	
def analyzesubs(subs):
	allsubs = [s.text for s in subs]
	corpus = ''.join(allsubs)

	corpus = corpus.replace('\n', '').replace('\u200e', '')
	corpus = corpus.lower()
	pattern = "(\.-)"
	corpus = re.sub(pattern, ' ', corpus)
	pattern=r"(\.)"
	corpus = re.sub(pattern, ' ', corpus)
	corpus
	pattern = r"\!"
	corpus = re.sub(pattern, '! ', corpus)
	pattern = r"\?"
	corpus = re.sub(pattern, '? ', corpus)
	pattern = r"\:"
	corpus = re.sub(pattern, ': ', corpus)
	pattern = r"\]"
	corpus = re.sub(pattern, '] ', corpus)
	nlp = spacy.load("en_core_web_sm")
	doc = nlp(corpus)
	pos = [(token.text, token.pos_) for token in doc]
	df = pd.DataFrame(pos, columns = ['word','pos'])

	return df

def analyze():
	return None



def searchword(word='sorry'):
	results = [i for i in subs if word in i.text]
	
	return st.write(len(results), ' mentions of ', word, ' found.')
	
def wordfamily():
	return family
	
def plotpie(df):

	# Pie chart, where the slices will be ordered and plotted counter-clockwise:
	labels = df.level.dropna().unique()
	sizes = df.groupby('level')['mentions'].sum()
	#explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

	fig1, ax1 = plt.subplots()
	ax1.bar(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
	ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

	return st.pyplot(fig1)

def plotbar(df):
	y = df['level'].dropna().value_counts()
	#st.write(y)
	labels = df.level.dropna().unique()
	#st.write(labels)
	chart_data = pd.DataFrame(y,columns=labels)
	#st.write(chart_data)
	#chart_data = pd.DataFrame(
	#np.random.randn(50, 3),
	#columns=["a", "b", "c"])
	return st.bar_chart(chart_data)

    
posdic = {'VERB': 'verb','ADJ': 'adjective','ADV': 'adverb','AUX': 'auxiliary','CONJ': 'conjunction','CCONJ': 'coordinating conjunction',
'DET': 'determiner','INTJ': 'interjection','NOUN': 'noun','NUM': 'numeral','PART': 'particle',
'PRON': 'pronoun','PROPN': 'proper noun','PUNCT': 'punctuation','SCONJ': 'subordinating conjunction',
'SYM': 'symbol','X': 'other', 'ADP': 'adposition'}

if __name__ == "__main__":
	selected_episode = select_episode()
	
	subs = loadsubs(selected_episode)
	df = analyzesubs(subs)
	main(df)

