#MD目录导入

import os
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

faq_dir=os.environ.get("FAQ_PATH")
collection_name=os.environ.get("COLLECTION_NAME")

loader = DirectoryLoader(faq_dir, glob="**/*.md")

data = loader.load()

# 初始化文本分割器
text_splitter = RecursiveCharacterTextSplitter(
  chunk_size=1000,
  chunk_overlap=100
)

texts = text_splitter.split_documents(data)


embeddings = OpenAIEmbeddings()

# PG Vector 向量存储库
from langchain.vectorstores.pgvector import PGVector
CONNECTION_STRING = PGVector.connection_string_from_db_params(
    driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
    host=os.environ.get("PGVECTOR_HOST", "localhost"),
    port=int(os.environ.get("PGVECTOR_PORT", "5433")),
    database=os.environ.get("PGVECTOR_DATABASE", "postgres"),
    user=os.environ.get("PGVECTOR_USER", "postgres"),
    password=os.environ.get("PGVECTOR_PASSWORD", "mysecretpassword"),
)

#将文档存入向量
db = PGVector.from_documents(
    embedding=embeddings,
    documents=data,
    collection_name=collection_name,
    connection_string=CONNECTION_STRING,
)

print("done")