# Consulting-Website-Analysis

This repository contains Python code for extracting textual data from websites and performing sentiment analysis to compute various metrics.

**Objective:**

Develop a system to automatically analyze text content from websites.
Extract article text, excluding headers, footers, and extraneous website elements.
Compute sentiment scores (positive, negative, polarity, subjectivity) and readability metrics (average sentence length, FOG Index, etc.) for the extracted text.

**Functionality:**

**Web Scraping:**

Extracts article text from a list of provided URLs.

**Text Preprocessing:**
Cleans the extracted text, removing unnecessary elements like HTML tags, special characters, etc.
Focuses on capturing the core article content (title and body text).

**Sentiment Analysis:**
Leverages NLP techniques to analyze the sentiment of the extracted text.
Calculates sentiment scores (positive, negative, polarity, subjectivity) using libraries like TextBlob, VADER, or NLTK.

**Readability Analysis:**
Computes various readability metrics like average sentence length, FOG Index, average number of words per sentence, etc.
Provides insights into the complexity and ease of understanding of the text.
