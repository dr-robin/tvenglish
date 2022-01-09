import streamlit as st
import pandas as pd
import numpy as np
import os
import pysrt
import spacy
import vlc
import time

st.title('British drama word study')

def getfiles():
    files = glob2.glob('srt/*.srt')
    return files

def gettitle(file):
    title = re.match("([A-Z]).*(?=S0)",file)[0].replace('.', ' ')
    episode = re.search("(\w\d\d\w\w\d)", file)[0]
    return title, episode

def loadsubs(file):
	subs = pysrt.open(file)
	allsubs = [s.text for s in subs]
	corpus = ' '.join(allsubs)
	corpus = corpus.replace('\n', '').replace('\u200e', '').replace("\\","")
	return corpus, subs

def batchload():
    files = getfiles()
    allcorpus=[]
    allsubs=[]
    for file in files:
        corpus, subs = loadsubs(file)
        allcorpus.append(corpus)
        allsubs.append(subs)
    return allcorpus, allsubs

def batchanalyze():
    for c in allcorpus:
        tmp = analyze(str(corpus))
        print(len(tmp.word), ' total words in episode ', counter)
        print(len(tmp.word.unique()), ' unique words in episode ', counter)

def allsubs():
    allcorpus = []
    allsubs = []
    counter = 0
    files = getfiles()
    
    for s in files:
        
        counter += 1
        
        try:
            corpus, subs = loadsubs(s)
            tmp = analyze(str(corpus))
            print(len(tmp.word), ' total words in episode ', counter)
            print(len(tmp.word.unique()), ' unique words in episode ', counter)
            allcorpus.append(corpus)
            allsubs.append(subs)
        except Exception as e:
            print(e)
        continue
        
        
    return allcorpus, allsubs

def analyze():
	# Create English nlp object
    dfs = []
	nlp = spacy.load("en_core_web_sm")
    for i in allcorpus:
        doc = nlp(i)
        # Iterate over tokens in a Doc
        pos = [(token.text, token.pos_, episode[i]) for token in doc]
        df = pd.DataFrame(pos, columns = ['word','pos','episode'])
        dfs.append(df)
    df = pd.concat(dfs, axis=1)
	return df

def load_data(nrows=20):
	data = df
	lowercase = lambda x: str(x).lower()
	data.rename(lowercase, axis='columns', inplace=True)

#	if option == 'VERB':
#		option = 'VERB'
#	if option == 'ADJECTIVE':
#		option = 'ADJ'
#	if option == 'NOUN':
#		option = 'NOUN'

#	data = data[data.pos == option]
	return data

def searchword(word='fucking'):
	results = [i for i in subs if word in i.text]
	print(len(results), ' mentions of ', word, ' found.')
	return results

#Streamlit code
files = getfiles()
allcorpus, allsubs = allsubs()
title, episode = [gettitle(f) for f in files]
df = analyze()


st.write('Study words in ', title)
data = load_data(nrows=20)

st.subheader('Words')

option = st.selectbox('Word type',('VERB', 'ADJECTIVE', 'NOUN'))
st.write('You selected:',option)
data = load_data(option)
st.write(data.value_counts())

@st.cache
def convert_df(df):
	return df.to_csv().encode('utf-8')

csv = convert_df(df)

st.download_button(
"Press to Download",
csv,
key='download-csv')

#Load video file
video_file = open('this.way.up.s01e01.hdtv.x264-mtb[ettv].mkv', 'rb')
#TRY TO PARSE VIDEO TO BYTES
video_bytes = video_file.read()

st.video(video_bytes)

selectedword = st.selectbox('Select a word',df.word.unique() , index=0,
	 key=None, help=None, on_change=None,
	 args=None, kwargs=None)

results = searchword(selectedword)
st.write(results)
