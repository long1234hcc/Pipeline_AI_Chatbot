# from langchain.utilities import SQLDatabase
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.llms.base import LLM
from pydantic import Field
from typing import Optional, Any
import google.generativeai as genai


class ChatSessionWrapper(LLM):
    """
    Lớp bao bọc cho Google Generative AI (Gemini) để tích hợp với LangChain.
    """
    chat_session: Any = Field()  # Định nghĩa trường chat_session

    @property
    def _llm_type(self) -> str:
        return "google_genai"

    def _call(self, prompt: str, stop: Optional[list] = None) -> str:
        # Gửi prompt tới chat_session và nhận phản hồi
        response = self.chat_session.send_message(prompt)
        return response.text


def setup_langchain(db_user: str, db_password: str, db_host: str, db_name: str, api_key: str):
    """
    Cấu hình LangChain để truy vấn cơ sở dữ liệu MySQL.

    Args:
        db_user (str): Tên người dùng MySQL.
        db_password (str): Mật khẩu MySQL.
        db_host (str): Địa chỉ host của MySQL (vd: localhost:3306).
        db_name (str): Tên cơ sở dữ liệu.
        api_key (str): API key của Google Generative AI.

    Returns:
        db_chain: Đối tượng SQLDatabaseChain đã cấu hình.
    """
    # Cấu hình API Google Generative AI
    genai.configure(api_key=api_key)

    # Tạo model Generative AI
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    # Khởi tạo chat session
    chat_session = model.start_chat()

    # Tạo đối tượng LLM từ chat session
    llm = ChatSessionWrapper(chat_session=chat_session)

    # Kết nối đến cơ sở dữ liệu MySQL
    db = SQLDatabase.from_uri(
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",
        sample_rows_in_table_info=3
    )

    # Tích hợp LangChain với cơ sở dữ liệu
    db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

    return db_chain
