from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.llms.base import LLM
from langchain.schema import LLMResult, Generation
from typing import Any, Optional, List
from pydantic import Field
import google.generativeai as genai


def connect_langchain_sql(db_user, db_password, db_host, db_name):
    try:
        db_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
        db = SQLDatabase.from_uri(db_uri, sample_rows_in_table_info=3)
        print("Kết nối LangChain tới MySQL thành công!")
        return db
    except Exception as e:
        print(f"Lỗi khi kết nối LangChain tới MySQL: {e}")
        raise


class ChatSessionWrapper(LLM):
    chat_session: Any = Field()  # Định nghĩa trường chat_session

    @property
    def _llm_type(self) -> str:
        return "google_genai"

    def _call(self, prompt: str, stop: Optional[list] = None) -> str:
        # Gửi prompt tới chat_session và nhận phản hồi
        response = self.chat_session.send_message(prompt)
        return response.text



def setup_chat_model(api_key):
    genai.configure(api_key=api_key)
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 1000,
    }
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    chat_session = model.start_chat()
    print("Cấu hình mô hình AI thành công!")
    return ChatSessionWrapper(chat_session=chat_session)


def query_with_langchain(db_chain, question):
    try:
        print(f"Đang thực hiện truy vấn: {question}")
        result = db_chain.run(question)
        print("Kết quả truy vấn:")
        return result
    except Exception as e:
        print(f"Lỗi khi thực hiện truy vấn: {e}")
        raise
