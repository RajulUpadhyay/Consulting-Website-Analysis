# -*- coding: utf-8 -*-
"""
Created on Tue Apr  20 11:43:58 2024

@author: rajul
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import os
import nltk
from nltk import tokenize
from nltk.corpus import stopwords
import re
import time

nltk.download('punkt', quiet=True)  # Download sentence tokenizer model
nltk.download('stopwords', quiet=True)  # Download stopwords corpus


current = time.time()

def word_type(file,kind):
    global words
    
    with open(file, 'r') as file:
            for line in file:
              line = line.strip()  # Remove leading/trailing whitespace
        
              if not line:  # Skip empty lines
                continue
        
              if "|" in line:  # Line defines a new category
                category1, category2 = line.split("|")
                
                words[category1.strip().lower()] = kind
                words[category2.strip().lower()] = kind

              else:
                category = line.strip()
                words[category.strip().lower()] = kind

def get_data(working_dir,url,url_id):

    try:
        page = urlopen(url)
    
    except:
        return -1
        
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    try:
        title = soup.find('title').text
    except:
        title = soup.find('h1').get_text()
        
    title = title[:-23]

    article_div = soup.find('div', class_='td-post-content tagdiv-type')
    
    if article_div:
        article_text = article_div.get_text()
        
    else:
        article_text = ""
        try:
          for p in soup.find_all('p'):
            article_text += p.get_text()
        
        except:
            print("The div could not be found.")
            return -1
        
    with open(f'{working_dir}/Extracted_files/{url_id}.txt','w', encoding="utf-8") as file:
        file.write(title)
        file.write('\n')
        file.write(article_text)
    
    article_text = tokenize.sent_tokenize(article_text)
    article_text.pop()
    article_text.append(title)
    
    return article_text

  
def sentiment_analysis(article_text,words):
    positive_score = 0
    negative_score = 0
    polarity_score = 0
    subjectivity_score = 0
    word_count = 0
    
    for text in article_text:
        sentence = tokenize.word_tokenize(text)
    
        for word in sentence:
            word = re.sub(r'[^\w]+$', '', word)
            word = word.strip().lower()
    
            if word not in words:
                # If word is not found in dictionary -> Skipped
                continue
            
            elif words[word]=='positive':
                positive_score += 1
            
            elif words[word] == 'negative':
                negative_score += 1
            
            else: 
                # This step skips any word which is a stop word from furthur analysis
                continue
            
            word_count+=1
            
    polarity_score = (positive_score - negative_score)/(positive_score + negative_score + 0.000001)
        
    subjectivity_score = (positive_score - negative_score)/ ((word_count) + 0.000001)

    return positive_score, negative_score, polarity_score, subjectivity_score



def words_count(article_text):
    stop_words = set(stopwords.words('english'))
    word_tokens = list()
    filtered_sentence = list()
    
    for text in article_text:
        sentence = tokenize.word_tokenize(text)
    
        for word in sentence:
            word = re.sub(r'[^\w]+$', '', word)
            word = word.strip().lower()
            if len(word)==0: continue
            word_tokens.append(word)
        
    filtered_sentence = [w for w in word_tokens if w.isalpha() and w.lower() not in stop_words]
    
    count = len(filtered_sentence) 
    return count

 
def rest_analysis(article_text):
    sentence_count = 0
    word_count = 0
    complex_count = 0
    total_syllable_count = 0
    total_personal_pronouns = 0
    char_count = 0
    

    for text in article_text:
        
        sentence = tokenize.word_tokenize(text)
        sentence_count +=1
        
        for word in sentence:
            word = re.sub(r'[^\w]+$', '', word)
            word = word.strip().lower()
            
            word_count += 1

            char_count += len(word)
        
        
            # Syllable word calculation
            if word[-2:] == 'es' or  word[-2:] == 'ed':
                word = word[:-2]
            
            syllable_count = len(re.findall('(?!e$)[aeiouy]+', word, re.I) + 
                                 re.findall('^[^aeiouy]*e$', word, re.I))
            
            total_syllable_count += syllable_count
            
            # Complex word calculation
            if syllable_count>1:
                complex_count += 1
            
            # Personal Pronoun calculation
            pronouns = ["I", "we", "my", "ours", "us"]
            pronoun_counts = 0
          
            for pronoun in pronouns:
              pronoun_counts += len(re.findall(rf"\b{pronoun}\b", text, re.IGNORECASE))
          
            # Exclude "US" if it's capital case
            pronoun_counts -= len(re.findall(r"\bUS\b", text))
            
            total_personal_pronouns += pronoun_counts
    
    
    return sentence_count, word_count, complex_count, total_syllable_count, total_personal_pronouns, char_count 
        
        
working_dir = 'C:/Users/rajul/Desktop/Blackcoffer'

# os.mkdir(f'{working_dir}/Extracted_files')

#Making a dictionary to append the words 
words = dict()

for folder in ['StopWords', 'MasterDictionary']:

    directory = f'{working_dir}/{folder}'
    
    for file in os.listdir(directory):
        if folder == 'StopWords':
            word_type(f'{directory}/{file}','Stopword')
            
        else:
            if file == 'negative-words.txt':
                word_type(f'{directory}/{file}','Negative')
            
            else: word_type(f'{directory}/{file}','Positive')



input_urls = pd.read_excel(f'{working_dir}/Input.xlsx')
output_sheet = pd.read_excel(f'{working_dir}/Output Data Structure.xlsx')

for i in range(len(input_urls)):
    print(i)
    url,url_id = input_urls['URL'][i],input_urls["URL_ID"][i]
    
    article_text = get_data(working_dir, url, url_id)
    
    if article_text == -1:
        print('error fetching data')
        continue
    
    # 1. Sentiment Analysis
    (positive_score, negative_score, polarity_score, 
         subjectivity_score) = sentiment_analysis(article_text,words)
    
    output_sheet['POSITIVE SCORE'][i] = positive_score
    output_sheet['NEGATIVE SCORE'][i] = negative_score
    output_sheet['POLARITY SCORE'][i] = polarity_score
    output_sheet['SUBJECTIVITY SCORE'][i] = subjectivity_score
    
    # 5. word count
    clean_word_count = words_count(article_text)
    
    output_sheet['WORD COUNT'][i] = clean_word_count
    
    # 2	Analysis of Readability
    (sentence_count, word_count, complex_count, total_syllable_count, 
         total_personal_pronouns, char_count) = rest_analysis(article_text)
    
    avg_sentence_length = round(word_count / sentence_count,2)
    
    percentage_complex_words = round(complex_count / word_count,2)
    
    fog_index = round(0.4* (avg_sentence_length + percentage_complex_words), 2)
    
    output_sheet['AVG SENTENCE LENGTH'][i] = avg_sentence_length
    output_sheet['PERCENTAGE OF COMPLEX WORDS'][i] = percentage_complex_words
    output_sheet['FOG INDEX'][i] = fog_index
    
    # 3	Average Number of Words Per Sentence
    avg_words_per_sentence = round(word_count / sentence_count, 2)
    
    output_sheet['AVG NUMBER OF WORDS PER SENTENCE'][i] = avg_words_per_sentence
    
    # 4 Complex Word Count
    output_sheet['COMPLEX WORD COUNT'][i] = complex_count
    
    # 6	Syllable Count Per Word
    syllable_per_word = round(total_syllable_count / word_count, 2)
    
    output_sheet['SYLLABLE PER WORD'][i] = syllable_per_word
    
    # 7	Personal Pronouns
    output_sheet['PERSONAL PRONOUNS'][i] = total_personal_pronouns
    
    # 8	Average Word Length
    avg_word_length = round(char_count / word_count,2)
    
    output_sheet['AVG WORD LENGTH'][i] = avg_word_length
    
    
output_sheet.to_excel(f'{working_dir}/Output Data Structure.xlsx', index = None)
end = time.time()
time_taken = (end - current)/60
print('Time taken in mins:',time_taken)
    
