# import libraries
import sys
from sqlalchemy import create_engine
import nltk
nltk.download(['punkt', 'wordnet'])

import re
import numpy as np
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputClassifier
import pickle


def load_data(database_filepath):
    #load data from given database 
    
    engine = create_engine('sqlite:///' + database_filepath)
    df = pd.read_sql_table('ETL_Preparation', engine)

    X = df.message
    y = df[df.columns[4:]]
    category_names = y.columns
    
    return X, y, category_names

def tokenize(text):
    
    #Punctuation removal
    url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    detected_urls = re.findall(url_regex, text)
    for url in detected_urls:
        text = text.replace(url, "urlplaceholder")
    
    #tokenize messages
    tokens = word_tokenize(text)
    
    #initiate lemmatizer
    lemmatizer = WordNetLemmatizer()

    #lemmatize tokens 
    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens


def build_model():
    
    # building pipeline using randomforest classifier, TF-idf transformer and count vectorizer (Convert a collection of text documents to a matrix of token counts)
    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=tokenize)),
        ('tfidf', TfidfTransformer()),
        ('clf', MultiOutputClassifier(RandomForestClassifier()))
    ])

    pipeline.get_params()
    
    #changing some pipeline parameters
    parameters = {
       'clf__estimator__n_estimators': [10, 20, 40],
       'clf__estimator__min_samples_split': [2, 3, 4],
    
    }
    
    #use gridsearchcv to pick up best parameters for the model
    cv = GridSearchCV(pipeline, param_grid=parameters, verbose=2, n_jobs=-1)
    
    return(cv)
    
def evaluate_model(model, X_test, Y_test, category_names):
    
    #run model
    Y_pred = model.predict(X_test)
    
    #print model scores for each category
    
    for i in range(36):
        print(Y_test.columns[i], ':')
        print(classification_report(Y_test.iloc[:,i], Y_pred[:,i]), '...................................................')



def save_model(model, model_filepath):
    
    #save model in a pickle file
    with open(model_filepath, 'wb') as file:
        pickle.dump(model, file)


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()
