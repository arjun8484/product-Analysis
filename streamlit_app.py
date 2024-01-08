import streamlit as st
import pandas as pd
import openai
import re

def convert(text, user_topic):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant that is going to extract product features from a list of e-commerce reviews. User will input a list of reviews and you will return the higher level product features that are being talked about in the reviews. Your output should be of the format - [......]. If there are no brand names mentioned, just simply return - [None]. Please make sure the output is in English and please make sure that the brands are within 1 square bracket."},
            {"role": "user", "content": f"{text}\n\nWhat product features are being talked about in the above list of reviews?"}
        ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content

    return result

def convert2(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant that is going to extract 15-20 higher level product features from a list of product features. Please state the higher level product features in a string format. Please follow the output format - ....,.....,...etc"},
            {"role": "user", "content": f"{text}\n\nWhat are the higher level product features from the above list of product features?"}
        ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content
    return result

def convert3(text, subthemes):
    sub_str = ", ".join(subthemes)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant that is going to classify a text into one of the user given themes. User will input a text and a list of themes and you will classify the text into one of those themes. The list of user given themes are {subthemes}. Please only classify the text into one of the given themes and don't come up with any new theme on your own. Please do not classify the text into more than 2-3 of the given themes. If the text does not fit any of the user given themes, then please return none. Your output should be in the format - [......]. Please make sure the output is in English and please make sure that the output is within 1 square bracket."},
            {"role": "user", "content": f"{text}\n\nWhich user given theme does the above text classify into?"}
        ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content

    return result

def process_reviews(user_topic):
    my_list = user_topic.split('\n')
    start = 0
    end = len(my_list)
    step = 30
    ss = []

    for i in range(start, end, step):
        x = i
        ss.append(my_list[x:x+step])

    results = []
    y = 0
    for text in ss:
        try:
            response = convert(text, user_topic)
        except:
            try:
                response = convert(text, user_topic)
            except:
                response = convert(text, user_topic)
        results.append(response)
        y = y+1

    return results

def main():
    st.title('Product Feature Extraction App')

    df = pd.read_excel('/content/Air Fryer reviews.xlsx')

    openai.api_key = "sk-Re8Kh3SC9E8RJwgdkwdMrsu8ZURO0VAGSOSKWVCi"

    user_topic = st.text_area('Enter the list of reviews:', '')

    if st.button('Extract Product Features'):
        results = process_reviews(user_topic)
        display_results(results, df)

def display_results(results, df):
    st.subheader('Results:')
    dd = pd.DataFrame({"Data": results})
    dd["Data"] = dd["Data"].apply(lambda x: x.strip("[]").split(","))
    dd = dd.explode(["Data"])

    subthemes = convert2(dd["Data"])
    
    results = []
    y = 0
    for text in df['Review Text'][len(results):]:
        try:
            response = convert3(text, subthemes)
        except:
            try:
                response = convert3(text, subthemes)
            except:
                response = convert3(text, subthemes)
        results.append(response)
        y = y+1

    ss = []
    for i in df['Output']:
        if 'None' in i:
            ss.append('None')
        elif 'none' in i:
            ss.append('None')
        else:
            res = re.findall(r'\[.*?\]', i)
            if len(res) == 0:
                ss.append('None')
            elif len(res) == 1:
                ss.append(res[0])
            else:
                ss.append(str(res))

    df['Product Features'] = ss
    df['Product Features'] = df['Product Features'].apply(lambda x: x.replace('[','').replace(']','').replace('@','').replace('"','').replace('#','').replace("'","").split(","))
    df = df.explode(['Product Features'])
    df['Product Features'] = df['Product Features'].apply(lambda x: x.lstrip().rstrip().lower())
    st.dataframe(df)

if __name__ == '__main__':
    main()
