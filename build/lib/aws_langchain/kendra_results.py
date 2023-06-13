from langchain.docstore.document import Document
import boto3
import re

def clean_result(res_text):
    res = re.sub("\s+", " ", res_text).replace("...","")
    return res
    
def get_top_n_results(resp, count):
    r = resp["ResultItems"][count]
    doc_title = r["DocumentTitle"]["Text"]
    doc_uri = r["DocumentURI"]
    r_type = r["Type"]
    if (r["AdditionalAttributes"] and r["AdditionalAttributes"][0]["Key"] == "AnswerText"):
        res_text = r["AdditionalAttributes"][0]["Value"]["TextWithHighlightsValue"]["Text"]
    else:
        res_text = r["DocumentExcerpt"]["Text"]
    doc_excerpt = clean_result(res_text)
    combined_text = "Document Title: " + doc_title + "\nDocument Excerpt: \n" + doc_excerpt + "\n"
    return {"page_content":combined_text, "metadata":{"source":doc_uri, "title": doc_title, "excerpt": doc_excerpt, "type": r_type}}

# 解析QUERY_ANSWER形式的答案
def get_top_n_query_answer(resp, count):
    r = resp["ResultItems"][count]
    doc_title = r["DocumentTitle"]["Text"]
    doc_uri = r["DocumentURI"]
    r_type = r["Type"]
    question_text = ""
    if (r["AdditionalAttributes"] and r["AdditionalAttributes"][0]["Key"] == "QuestionText"):
        question_text = r["AdditionalAttributes"][0]["Value"]["TextWithHighlightsValue"]["Text"]


    if (r["AdditionalAttributes"] and r["AdditionalAttributes"][1]["Key"] == "AnswerText"):
        res_text = r["AdditionalAttributes"][1]["Value"]["TextWithHighlightsValue"]["Text"]
    else:
        res_text = r["DocumentExcerpt"]["Text"]
    doc_excerpt = clean_result(res_text)
    combined_text = "问题: " + question_text + "\n答案:" + doc_excerpt + "\n评分:" + r["ScoreAttributes"]["ScoreConfidence"] + "\n"
    return {"page_content": combined_text,
            "metadata": {"source": doc_uri, "title": doc_title, "excerpt": doc_excerpt, "type": r_type}}


def kendra_query(kclient, kquery, kcount, kindex_id):
    #response = kclient.query(IndexId=kindex_id, QueryText=kquery.strip())
    print("----kendra_query----")
    print(kquery)
    print("----kendra_query----")
    # print(kindex_id)
    response = kclient.query(
            IndexId=kindex_id, 
            QueryText=kquery.strip(),
            AttributeFilter = {
            "EqualsTo": {
                "Key": "_language_code",
                "Value": {
                    "StringValue": "zh"
                    }
                }
            },
            QueryResultTypeFilter="QUESTION_ANSWER"
    )

    if len(response["ResultItems"]) > kcount:
        r_count = kcount
    else:
        r_count = len(response["ResultItems"])
    docs = [get_top_n_query_answer(response, i) for i in range(0, r_count)] #取最新的一个
    return [Document(page_content = d["page_content"], metadata = d["metadata"]) for d in docs]

def kendra_client(kindex_id, kregion):
    kclient = boto3.client('kendra', region_name=kregion)
    return kclient

