# from ..base_retriever import BaseRetriever

from sqlalchemy import (
    create_engine,
    insert,
    MetaData,
    Table,
    Column,
    String,
)

from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import NLSQLRetriever


class TextToSQLRetriever:
    def __init__(self, sql_database=None):
        # super().__init__(data, retrieval_size)
        self.sql_database = sql_database
        if not sql_database:
            self._create_db()
        self.llm = OpenAI(temperature=0.1, model="gpt-4.1-mini")
        self.nl_sql_retriever = NLSQLRetriever(
            self.sql_database, tables=["ex_rules"], llm=self.llm, return_raw=False
        )
        self.query_engine = RetrieverQueryEngine.from_args(
            self.nl_sql_retriever, llm=self.llm
        )

    def retrieve(self, query):
        # Implement RAG retrieval logic here
        response = self.query_engine.query(query)
        return response

    def _create_db(self):
        engine = create_engine("sqlite:///:memory:")
        metadata_obj = MetaData()

        # create city SQL table
        table_name = "ex_rules"
        ex_rules_table = Table(
            table_name,
            metadata_obj,
            Column("expense_name", String(16), primary_key=True),
            Column("account", String(16), nullable=False),
            # Column("advance application", String(16), nullable=False),
            # Column("Memo section", String(16), nullable=True)
        )
        metadata_obj.create_all(engine)
        self.sql_database = SQLDatabase(engine, include_tables=["ex_rules"])

        rows = [
            {
                "expense_name": "Travel expenses: (Domestic) Local trains and buses only",
                "account": "Travel expenses and transportation expenses",
            },
            {
                "expense_name": "Travel expenses: (overseas_not subject to consumption tax) Local trains and buses only",
                "account": "Travel expenses and transportation expenses(Support: Overseas)",
            },
            {
                "expense_name": "Travel expenses: (overseas subject to consumption tax)",
                "account": "Travel expenses and transportation expenses(Support: Overseas)",
            },
            {
                "expense_name": "Company food and drink expenses (reduced tax rate 8%): Only company members can participate (excluding Happy Hour and general meeting social gatherings)",
                "account": "Entertainment and social expenses(Subsidy: Internal entertainment and social expenses)",
            },
            {
                "expense_name": "Communication costs: postage (stamps, etc.), motorcycle courier, courier service - subject to consumption tax",
                "account": "communication costs",
            },
        ]
        for row in rows:
            stmt = insert(ex_rules_table).values(**row)
            with engine.begin() as connection:
                cursor = connection.execute(stmt)


if __name__ == "__main__":
    query_str = "Return the top 3 expense name(s) for travel"
    text2_sql = TextToSQLRetriever()
    answer = text2_sql.retrieve(query_str)
    print(answer)
