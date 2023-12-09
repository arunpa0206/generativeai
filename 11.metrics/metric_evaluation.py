# -*- coding: utf-8 -*-
"""Metric _evaluation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1d_tuvmBEspzzIU374koRGdPJ8Srvxvd7
"""

#Import generic libraries
import numpy as np
import pandas as pd
import torch

news = pd.read_csv("articles.csv")
DOCUMENT="Article Body"
MAX_NEWS = 3
subset_news = news.head(MAX_NEWS)
subset_news.head()

articles = subset_news[DOCUMENT].tolist()

#Load the Models and create the summaries
import transformers
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name_small = "t5-base"
model_name_reference = "flax-community/t5-base-cnn-dm"#To determine which model generates better summaries, we will utilize a well-known dataset called 'cnn_dailymail,'

#This function returns the tokenizer and the Model.
def get_model(model_id):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

    return tokenizer, model

tokenizer_small, model_small = get_model(model_name_small)

tokenizer_reference, model_reference = get_model(model_name_reference)

def create_summaries(texts_list, tokenizer, model, max_l=125):

    # We are going to add a prefix to each article to be summarized
    # so that the model knows what it should do
    prefix = "Summarize this news: "
    summaries_list = [] #Will contain all summaries

    texts_list = [prefix + text for text in texts_list]

    for text in texts_list:

        summary=""

        #calculate the encodings
        input_encodings = tokenizer(text,max_length=1024,return_tensors='pt',padding=True,truncation=True)



       # Generate summaries
        with torch.no_grad():
            output = model.generate(input_ids=input_encodings.input_ids,
                attention_mask=input_encodings.attention_mask,
                max_length=max_l,  # Set the maximum length of the generated summary
                num_beams=2,     # Set the number of beams for beam search
                early_stopping=True)
#Decode to get the text
        summary = tokenizer.batch_decode(output, skip_special_tokens=True)

        #Add the summary to summaries list
        summaries_list += summary
    return summaries_list

# Creating the summaries for both models.
summaries_small = create_summaries(articles,tokenizer_small, model_small)
summaries_reference = create_summaries(articles,tokenizer_reference,model_reference)
summaries_small

summaries_reference

#!pip install evaluate
#!pip install rouge_score

import evaluate
from nltk.tokenize import sent_tokenize

#With the function load of the library evaluate
#we create a rouge_score object
rouge_score = evaluate.load("rouge")

def compute_rouge_score(generated, reference):

    #We need to add '\n' to each line before send it to ROUGE
    generated_with_newlines = ["\n".join(sent_tokenize(s.strip())) for s in generated]
    reference_with_newlines = ["\n".join(sent_tokenize(s.strip())) for s in reference]

    return rouge_score.compute(
        predictions=generated_with_newlines,
        references=reference_with_newlines,
        use_stemmer=True,)

import nltk
nltk.download('punkt')
print(compute_rouge_score(summaries_small, summaries_reference))
