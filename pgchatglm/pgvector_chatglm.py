import os
import json

from langchain.chains import ConversationalRetrievalChain
from langchain.chains import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
from langchain.llms import OpenAI
from langchain.llms.sagemaker_endpoint import LLMContentHandler, SagemakerEndpoint
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.vectorstores.pgvector import PGVector


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


MAX_HISTORY_LENGTH = 5
OPENAI_KEY = os.environ["OPENAI_API_KEY"]
endpoint_name = os.environ["ENDPOINT_NAME"]

prompt_template = """
假设你是一个POS系统客服人员，你有以下信息:
-------
{context}
-------

请根据以上的信息严格回答问题: {question}？
"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

_template = """
  给定以下对话和一个后续问题，将后续问题重述为一个独立的问题。

  对话:
  {chat_history}
  
  后续问题: {question}
  
  标准问题:
  """
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

# 构造大语言模型
def build_llm():
    class ContentHandler(LLMContentHandler):
        content_type = "application/json"
        accepts = "application/json"
        def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
            input_str = json.dumps({"ask": prompt})
            print(prompt)
            return input_str.encode('utf-8')

        def transform_output(self, output: bytes) -> str:
            response_json = json.loads(output.read())
            return response_json["answer"]

    contentHandler = ContentHandler()

    llm = SagemakerEndpoint(
        endpoint_name=endpoint_name,
        region_name='ap-southeast-1',
        content_handler=contentHandler
    )
    return llm;

def build_retriever(collection_name="annil-pos-faq-prod"):
    # PG Vector 向量存储库
    CONNECTION_STRING = PGVector.connection_string_from_db_params(
        driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
        host=os.environ.get("PGVECTOR_HOST", "localhost"),
        port=int(os.environ.get("PGVECTOR_PORT", "5433")),
        database=os.environ.get("PGVECTOR_DATABASE", "postgres"),
        user=os.environ.get("PGVECTOR_USER", "postgres"),
        password=os.environ.get("PGVECTOR_PASSWORD", "mysecretpassword"),
    )
    # embeddings = OpenAIEmbeddings()
    from langchain.vectorstores.pgvector import DistanceStrategy
    store = PGVector(
        connection_string=CONNECTION_STRING,
        embedding_function=OpenAIEmbeddings(),
        collection_name=collection_name,
        distance_strategy=DistanceStrategy.COSINE
    )

    retriever = store.as_retriever()
    retriever.search_kwargs = {'k': 2} #dict 省钱的秘诀
    return retriever;

def build_chain():
    #历史存储器
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # 大语言模型
    llm = build_llm();

    #问题产生器 - 这个是产生多次问题的的时候的Prompt, 根据History来产生问题
    question_generator = LLMChain(llm=OpenAI(), prompt=CONDENSE_QUESTION_PROMPT, verbose=True)

    # 这种方式只针对stuff才有效
    qa_chain = load_qa_chain(llm=llm, chain_type="stuff", prompt=PROMPT, verbose=True)

    qa = ConversationalRetrievalChain(
        retriever=build_retriever(), #pgvector
        question_generator=question_generator, #问题产生器
        combine_docs_chain=qa_chain, # 根据知识召回的数据， 让LLM组织语言回答
        verbose=True,
        memory=memory #历史记录器
    )
    return qa

    # return qa


def run_chain(chain, prompt: str, history=[]):
    return chain({"question": prompt, "chat_history": history})


if __name__ == "__main__":
    qa = build_chain()
    run_chain(qa, "你好", history=[])
    #print(pp['answer'])