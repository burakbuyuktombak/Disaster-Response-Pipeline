import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    """
    INPUT:
    messages_filepath - path to messages csv file
    categories_filepath - path to categories csv file
    
    OUTPUT:
    df - Merged data
    """    
    
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    df = pd.merge(messages, categories, on = 'id')
    
    return df

def clean_data(df):
    """
    INPUT:
    df - Merged data
    
    OUTPUT:
    df - Cleaned data
    """    
    
    categories = df['categories'].str.split(pat=';', expand = True)
    
    # select the first row of the categories dataframe
    row = categories.iloc[[1]]
    
    # use this row to extract a list of new column names for categories
    category_colnames = [category_name.split('-')[0] for category_name in row.values[0]]
    
    # rename the columns of 'categories'
    categories.columns = category_colnames
    
    # convert category values to just numbers 0 or 1
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].astype(str).str[-1:]
    
        # convert column from string to numeric
        categories[column] = categories[column].astype(int)
    
    # drop the original categories column from 'df'
    df.drop(['categories'], axis=1, inplace=True)
    
    # concatenate the original datafram with the new 'categories' dataframe
    df = pd.concat([df,categories], join='inner', axis=1)
    
    # drop duplicates
    df.drop_duplicates(inplace=True)
    
    # drop 'child_alone' column as it has only 0 values 
    df = df.drop('child_alone', axis = 1)
    
    # 'related' column has max value of 2, it could be error
    # therefore, we will replace '2' with '0'
    df['related'] = df['related'].map(lambda x: 0 if x==2 else x)
    
    return df


def save_data(df, database_filename):
    """
    INPUT:
    df - cleaned data
    database_filename - database filename for sqlite database with (.db) file type
    
    OUTPUT:
    None - save cleaned data into database
    """
    
    engine = create_engine('sqlite:///'+ database_filename)
    df.to_sql('ETL_Preparation', engine, index = False, if_exists = 'replace')

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()