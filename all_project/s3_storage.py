from minio import Minio
from minio.error import S3Error
from io import BytesIO
import pandas as pd

def connect_minio(endpoint, access_key, secret_key, secure=False):
    try:
        client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        print("Kết nối thành công đến MinIO!")
        return client
    except S3Error as e:
        print(f"Lỗi khi kết nối MinIO: {e}")
        raise

def create_bucket(client, bucket_name):
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' đã được tạo.")
        else:
            print(f"Bucket '{bucket_name}' đã tồn tại.")
    except S3Error as e:
        print(f"Lỗi khi tạo bucket: {e}")
        raise

def upload_file_to_s3(client, bucket_name, file_path, object_name):
    try:
        client.fput_object(bucket_name, object_name, file_path)
        print(f"File '{file_path}' đã được upload vào bucket '{bucket_name}' với tên '{object_name}'.")
    except S3Error as e:
        print(f"Lỗi khi upload file lên MinIO: {e}")
        raise

def upload_dataframe_to_s3(client, bucket_name, dataframe, object_name):
    """
    Upload pandas DataFrame trực tiếp lên MinIO.
    """
    try:
        # Chuyển DataFrame thành CSV trong bộ nhớ
        buffer = BytesIO()
        dataframe.to_csv(buffer, index=False)
        buffer.seek(0)

        # Upload buffer vào MinIO
        client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=buffer,
            length=buffer.getbuffer().nbytes,
            content_type='text/csv'
        )
        print(f"DataFrame đã được upload vào bucket '{bucket_name}' với tên '{object_name}'.")
    except S3Error as e:
        print(f"Lỗi khi upload DataFrame lên MinIO: {e}")
        raise
