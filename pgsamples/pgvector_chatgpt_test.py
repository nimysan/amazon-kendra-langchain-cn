import os
import json

from langchain.chains import ConversationalRetrievalChain, RetrievalQAWithSourcesChain
from langchain.chains import LLMChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.llms.sagemaker_endpoint import ContentHandlerBase, SagemakerEndpoint, LLMContentHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.vectorstores.pgvector import PGVector
import pydevd_pycharm

# pydevd_pycharm.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)

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

prompt_template = """

假设你是一个客服人员, 请严格根据如下指定的内容回答问题.

内容如下:

'''
{context}
'''

你需要回答的问题如下:

'''
{question}?
'''
-----
你需要按以下要求回答:
1. 如果问题与给定内容不匹配, 请回答“我不知道，请提问与CEIBA2系统相关的问题” 并结束回答;
2. 如果问题与给定内容有多个匹配, 请选择合适的回答
  """
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

_template = """
  给定以下对话和一个后续问题，将后续问题重述为一个独立的问题。

  对话:
  {chat_history}
  接下来的问题: {question}
  标准问题:
  """
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

stuff_prompt_template = """你好啊  试试这个 answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer in Italian:"""

stuff_question_prompt_template = """此AI是一位技术专家，会给出专业精准的回答。
    如果AI不能从以下信息中获得答案，请回答不知道，不要编造答案。
      
    信息: 
    {summaries}
      
    问题:
    {question} 
      
      
    以上的每条信息都是独立的，请基于以上信息给出专业且精准的回答。答案以"根据以上消息得知："开头。请用中文回答。
    如果没有在以上消息中获得答案，请回答不知道。
      
    Solution:"""
STUFF_PROMPT = PromptTemplate(
    template=stuff_question_prompt_template, input_variables=["summaries", "question"]
)

def build_retriever(collection_name):
    # PG Vector 向量存储库
    print("hello -- " + collection_name)
    if (collection_name == ''):
        raise "please give collection name"
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

    print("database connection is---> " + CONNECTION_STRING)
    retriever = store.as_retriever()
    retriever.search_kwargs = {'k': 2}  # dict 省钱的秘诀
    return retriever;


# 构造大语言模型
def build_llm(llm):
    if llm == "chatgpt":
        return OpenAI(batch_size=5);  # 大语言模型 map-reduce
    elif llm == 'chatglm':
        class ContentHandler(LLMContentHandler):
            content_type = "application/json"
            accepts = "application/json"

            def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
                input_str = json.dumps({"text_inputs": prompt})
                return input_str.encode('utf-8')

            def transform_output(self, output: bytes) -> str:
                # response_json = json.loads(output.read().decode("utf-8"))
                response_json = json.loads(output.read())
                print(response_json)
                # return response_json[0]["generated_text"]
                return response_json["generated_texts"][0]

        content_handler = ContentHandler()
        endpoint_name = os.environ.get("ENDPOINT_NAME")
        endpoint_region = os.environ.get("ENDPOINT_REGION", "us-east-1")

        print("endpoint_name " + endpoint_name)
        llm = SagemakerEndpoint(
            endpoint_name=endpoint_name,
            region_name=endpoint_region,
            model_kwargs={"temperature": 1e-10, "max_length": 500},
            content_handler=content_handler
        )
        return llm;
    else:
        raise ImportError(
            "please give correct llm type"
        )


def build_chain(llm="chatgpt"):
    # print("database collection name ---> " + collection_name)

    # 历史存储器
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # 大语言模型
    llm = build_llm(llm);

    # 问题产生器 - 这个是产生多次问题的的时候的Prompt, 根据History来产生问题
    question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT, verbose=True)

    template = """Given the following extracted parts of a long document and a question, create a final answer with references ("SOURCES"). 
    If you don't know the answer, just say that you don't know. Don't try to make up an answer.
    ALWAYS return a "SOURCES" part in your answer.
    Respond in Italian.

    QUESTION: {question}
    =========
    {summaries}
    =========
    FINAL ANSWER IN ITALIAN:"""
    PROMPT = PromptTemplate(template=template, input_variables=["summaries", "question"])
    # 这种方式只针对stuff才有效
    qa_chain = load_qa_with_sources_chain(llm=llm, chain_type="stuff", verbose=True, prompt=STUFF_PROMPT)

    # 这个是针对map_reduce的
    # qa_chain = load_qa_with_sources_chain(llm=llm, chain_type="map_reduce", question_prompt=PROMPT, verbose=True)

    collection_name = os.environ.get("COLLECTION_NAME")
    if collection_name == '':
        raise "please give collection name"

    print("knowledge bases on collection " + collection_name)
    qa = RetrievalQAWithSourcesChain(
        combine_documents_chain=qa_chain,
        retriever=build_retriever(collection_name),  # pgvector
        verbose=True
    )
    return qa

    # return qa

def run_chain(chain, prompt: str, history=[]):
    return chain({"question": prompt, "chat_history": history})


if __name__ == "__main__":
    qa = build_chain("chatgpt")
    pp = run_chain(qa, "怎么对小票做备注？", history=[])
    print(pp['answer'])
