import pandas as pd
import re

def clean_data(dataframe):
    """
    Làm sạch dữ liệu:
    - Loại bỏ giá trị NaN hoặc thay thế bằng giá trị mặc định.
    - Loại bỏ các ký tự đặc biệt trong cột văn bản.
    """
    print("Đang làm sạch dữ liệu...")
    # Thay thế NaN trong các cột quan trọng bằng giá trị mặc định
    dataframe['new_price'] = dataframe['new_price'].fillna(0)
    dataframe['old_price'] = dataframe['old_price'].fillna(0)
    dataframe['sold'] = dataframe['sold'].fillna(0)
    dataframe['vn_name'] = dataframe['vn_name'].fillna("Unknown")
    dataframe['en_name'] = dataframe['en_name'].fillna("Unknown")
    
    # Loại bỏ ký tự đặc biệt trong các cột văn bản
    for col in ['vn_name', 'en_name', 'discount']:
        dataframe[col] = dataframe[col].str.replace(r'[^\w\s%]', '', regex=True)

    return dataframe

def transform_data(dataframe):
    """
    Chuẩn hóa dữ liệu:
    - Chuyển đổi cột số sang dạng float/int.
    - Tách thông tin quan trọng từ các chuỗi văn bản (nếu cần).
    """
    print("Đang chuẩn hóa dữ liệu...")

    def extract_numbers(input_string):
        """
        Trích xuất số từ chuỗi và chuyển thành số thực.
        """
        try:
            # Nếu input là số
            return float(input_string)
        except ValueError:
            # Loại bỏ ký tự không phải số và tìm các số trong chuỗi
            clean_string = input_string.replace(".", "").replace(",", "")
            numbers = re.findall(r'\d+', clean_string)
            return float(numbers[0]) if numbers else None

    # Áp dụng trích xuất số cho các cột số
    dataframe['new_price'] = dataframe['new_price'].apply(extract_numbers)
    dataframe['old_price'] = dataframe['old_price'].apply(extract_numbers)
    dataframe['sold'] = dataframe['sold'].apply(extract_numbers)

    # Thêm cột tính toán (nếu cần)
    dataframe['discount_percentage'] = dataframe.apply(
        lambda row: ((row['old_price'] - row['new_price']) / row['old_price'] * 100)
        if row['old_price'] and row['new_price'] else 0, axis=1
    )

    return dataframe

def validate_data(dataframe):
    """
    Xác thực dữ liệu:
    - Kiểm tra các giá trị cần thiết không bị thiếu.
    - Đảm bảo dữ liệu không chứa giá trị bất thường.
    """
    print("Đang xác thực dữ liệu...")

    # Kiểm tra cột bắt buộc không được thiếu
    required_columns = ['new_price', 'old_price', 'vn_name', 'en_name', 'sold']
    for col in required_columns:
        if dataframe[col].isnull().any():
            raise ValueError(f"Cột '{col}' chứa giá trị bị thiếu!")

    # Loại bỏ các hàng có giá trị bất hợp lý (ví dụ: giá < 0)
    dataframe = dataframe[dataframe['new_price'] >= 0]
    dataframe = dataframe[dataframe['old_price'] >= 0]
    dataframe = dataframe[dataframe['sold'] >= 0]

    return dataframe
