from minio import Minio
from minio.error import S3Error

class S3Storage:
    def __init__(self, endpoint, access_key, secret_key, secure=False):
        """
        Khởi tạo kết nối MinIO.
        """
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

    def list_buckets(self):
        """
        Lấy danh sách các buckets.
        """
        try:
            buckets = self.client.list_buckets()
            return [(bucket.name, bucket.creation_date) for bucket in buckets]
        except S3Error as e:
            print("Lỗi khi liệt kê buckets:", e)
            return []

    def create_bucket(self, bucket_name):
        """
        Tạo bucket nếu chưa tồn tại.
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                print(f"Bucket '{bucket_name}' đã được tạo.")
            else:
                print(f"Bucket '{bucket_name}' đã tồn tại.")
        except S3Error as e:
            print(f"Lỗi khi tạo bucket '{bucket_name}':", e)

    def upload_file(self, bucket_name, object_name, file_path):
        """
        Upload file lên bucket MinIO.
        """
        try:
            self.client.fput_object(bucket_name, object_name, file_path)
            print(f"File '{file_path}' đã được upload vào bucket '{bucket_name}' với tên '{object_name}'.")
        except S3Error as e:
            print(f"Lỗi khi upload file '{file_path}' vào bucket '{bucket_name}':", e)
