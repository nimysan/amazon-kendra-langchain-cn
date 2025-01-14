from aws_langchain.kendra_index_retriever import KendraIndexRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain import SagemakerEndpoint
from langchain.llms.sagemaker_endpoint import ContentHandlerBase
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI # import OpenAI model

import sys
import json
import os

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

MAX_HISTORY_LENGTH = 1

def build_chain():
  region = os.environ["AWS_REGION"]
  kendra_index_id = os.environ["KENDRA_INDEX_ID"]
  endpoint_name = os.environ["CHATGLM_ENDPOINT"]
  OPENAI_KEY=os.environ["OPENAI_KEY"]

  class ContentHandler(ContentHandlerBase):
      content_type = "application/json"
      accepts = "application/json"

      def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
          #input_str = json.dumps({"inputs": prompt, "parameters": model_kwargs})
          print("这是进入模型的prompt")
          print(prompt)
          print("-------")
          input_str = json.dumps({"ask": prompt})
          return input_str.encode('utf-8')
      
      def transform_output(self, output: bytes) -> str:
          #response_json = json.loads(output.read().decode("utf-8"))
          response_json = json.loads(output.read())
          #return response_json[0]["generated_text"]
          return response_json["answer"]

  content_handler = ContentHandler()

  llm=SagemakerEndpoint(
          endpoint_name=endpoint_name, 
          region_name='ap-southeast-1',
          model_kwargs={"temperature":1e-10, "max_length": 500},
          content_handler=content_handler
      )
  llm = OpenAI(temperature=0.7, openai_api_key=OPENAI_KEY)
  print(kendra_index_id)
  print("region " + region)
  retriever = KendraIndexRetriever(kendraindex=kendra_index_id,
      awsregion=region, 
      return_source_documents=True)

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
1. 如果问题有歧义, 请回答 “报歉” 并结束回答;
2. 如果问题与给定内容不匹配, 请回答“我不知道，请提问与POS系统相关的问题” 并结束回答;
3. 如果问题与给定内容有多个匹配, 请挑选最合适的回答;
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


  qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, qa_prompt=PROMPT, condense_question_prompt=CONDENSE_QUESTION_PROMPT, return_source_documents=True)
  return qa

def run_chain(chain, prompt: str, history=[]):
  return chain({"question": prompt, "chat_history": history})


if __name__ == "__main__":
  chat_history = []
  qa = build_chain()
  print(bcolors.OKBLUE + "Hello! How can I help you?" + bcolors.ENDC)
  print(bcolors.OKCYAN + "Ask a question, start a New search: or CTRL-D to exit." + bcolors.ENDC)
  print(">", end=" ", flush=True)
  for query in sys.stdin:
    if (query.strip().lower().startswith("new search:")):
      query = query.strip().lower().replace("new search:","")
      chat_history = []
    elif (len(chat_history) == MAX_HISTORY_LENGTH):
      chat_history.pop(0)
    result = run_chain(qa, query, chat_history)
    chat_history.append((query, result["answer"]))
    print(bcolors.OKGREEN + result['answer'] + bcolors.ENDC)
    if 'source_documents' in result:
      print(bcolors.OKGREEN + 'Sources:')
      for d in result['source_documents']:
        print(d.metadata['source'])
    print(bcolors.ENDC)
    print(bcolors.OKCYAN + "Ask a question, start a New search: or CTRL-D to exit." + bcolors.ENDC)
    print(">", end=" ", flush=True)
  print(bcolors.OKBLUE + "Bye" + bcolors.ENDC)
