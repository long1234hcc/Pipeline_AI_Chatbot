import pandas as pd
import re


print("Cleaning")
def clean_data(dataframe):
    dataframe['new_price'] = dataframe['new_price'].fillna(0)
    dataframe['old_price'] = dataframe['old_price'].fillna(0)
    dataframe['sold'] = dataframe['sold'].fillna(0)
    dataframe['vn_name'] = dataframe['vn_name'].fillna("Unknown")
    dataframe['en_name'] = dataframe['en_name'].fillna("Unknown")
    
    # Remove special character
    for col in ['vn_name', 'en_name', 'discount']:
        dataframe[col] = dataframe[col].str.replace(r'[^\w\s%]', '', regex=True)

    return dataframe


print("Transform data...")
def transform_data(dataframe):

    def extract_numbers(input_string):
        try:
            return float(input_string)
        except ValueError:
            clean_string = input_string.replace(".", "").replace(",", "")
            numbers = re.findall(r'\d+', clean_string)
            return float(numbers[0]) if numbers else None

    dataframe['new_price'] = dataframe['new_price'].apply(extract_numbers)
    dataframe['old_price'] = dataframe['old_price'].apply(extract_numbers)
    dataframe['sold'] = dataframe['sold'].apply(extract_numbers)

    dataframe['discount_percentage'] = dataframe.apply(
        lambda row: ((row['old_price'] - row['new_price']) / row['old_price'] * 100)
        if row['old_price'] and row['new_price'] else 0, axis=1
    )

    return dataframe

def validate_data(dataframe):
    required_columns = ['new_price', 'old_price', 'vn_name', 'en_name', 'sold']
    for col in required_columns:
        if dataframe[col].isnull().any():
            raise ValueError(f"Cột '{col}' chứa giá trị bị thiếu!")

    dataframe = dataframe[dataframe['new_price'] >= 0]
    dataframe = dataframe[dataframe['old_price'] >= 0]
    dataframe = dataframe[dataframe['sold'] >= 0]

    return dataframe
