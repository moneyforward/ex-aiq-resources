from ..base_retriever import BaseRetriever
import os
import re
from sqlalchemy import (
    create_engine,
    insert,
    MetaData,
    Table,
    Column,
    String,
)
from llama_index.core import Settings
from llama_index.core import SQLDatabase
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import NLSQLRetriever

from dotenv import load_dotenv

load_dotenv()

Settings.embed_model = AzureOpenAIEmbedding(
    endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
    credential=os.getenv("AZURE_EMBEDDING_API_KEY"),
    model=os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME"),
)


def sanitize_column(col_name: str) -> str:
    safe = re.sub(r"[^0-9a-zA-Z_]", "_", col_name)  # replace spaces/special chars
    if safe[0].isdigit():
        safe = f"col_{safe}"
    return safe.lower()


class TextToSQLRetriever(BaseRetriever):
    def __init__(self, data, retrieval_size=3):
        super().__init__(data, retrieval_size)
        self.df = data
        self.engine = create_engine("sqlite:///:memory:")
        self.sql_database = None
        if not self.sql_database:
            self._create_db()
        self.llm = AzureOpenAI(
            temperature=0.1,
            engine="gpt-4.1-mini",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2025-01-01-preview",
        )
        self.nl_sql_retriever = NLSQLRetriever(
            self.sql_database,
            tables=["ex_rules"],
            llm=self.llm,
            embed_model=Settings.embed_model,
            return_raw=False,
        )
        self.query_engine = RetrieverQueryEngine.from_args(
            self.nl_sql_retriever, llm=self.llm
        )

    def retrieve(self, query):
        # Implement RAG retrieval logic here
        response = self.nl_sql_retriever.retrieve(query)
        answer = []
        for item in response:
            answer.append(item.metadata.get("rule_name", ""))
        return answer

    def _create_db(self):
        metadata_obj = MetaData()

        # create city SQL table
        table_name = "ex_rules"
        new_names = [
            "rule_name",
            "expense_name",
            "account",
            "expense_and_account_name",
            "advance_application",
            "receipt_attached",
            "eligibility_number",
            "contents_to_enter",
            "when_to_use_this_expense_item",
            "content_to_check",
        ]
        # if len(new_names) != len(self.df.columns):
        #     raise ValueError("Column length mismatch")
        # mapping = {col: new_names[i] for i, col in enumerate(self.df.columns)}
        mapping = dict(zip(self.df.columns, new_names))
        df = self.df.rename(columns=mapping)

        ex_rules_table = Table(
            table_name, metadata_obj, *[Column(col, String) for col in df.columns]
        )
        metadata_obj.create_all(self.engine)

        with self.engine.begin() as connection:
            for _, row in df.iterrows():
                stmt = insert(ex_rules_table).values(**row.to_dict())
                connection.execute(stmt)

        self.sql_database = SQLDatabase(self.engine, include_tables=["ex_rules"])

        # with self.engine.connect() as connection:
        #     result = connection.execute(ex_rules_table.select())
        #     rows = result.fetchall()
        #     for row in rows:
        #         print(row)
