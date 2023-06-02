import boto3
import pprint

kendra = boto3.client("kendra")

# Provide the index ID
index_id = "967eb751-b6d3-487e-85fe-d0ffcd92609d"
# Provide the query text
query = "同款串色了怎么处理"

response = kendra.query(
    QueryText=query,
    IndexId=index_id)

print("\nSearch results for query: " + query + "\n")

for query_result in response["ResultItems"]:

    print("-------------------")
    print("Type: " + str(query_result["Type"]))

    if query_result["Type"] == "ANSWER" or query_result["Type"] == "QUESTION_ANSWER":
        answer_text = query_result["DocumentExcerpt"]["Text"]
        print(answer_text)

    if query_result["Type"] == "DOCUMENT":
        if "DocumentTitle" in query_result:
            document_title = query_result["DocumentTitle"]["Text"]
            print("Title: " + document_title)
        document_text = query_result["DocumentExcerpt"]["Text"]
        print(document_text)

    print("------------------\n\n")  
