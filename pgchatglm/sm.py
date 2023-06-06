from typing import Dict, List
from langchain.embeddings import SagemakerEndpointEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler

import json


class ContentHandler(EmbeddingsContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, inputs: list[str], model_kwargs: Dict) -> bytes:
        input_str = json.dumps({"inputs": inputs, **model_kwargs})
        return input_str.encode('utf-8')

    def transform_output(self, output: bytes) -> List[List[float]]:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json["vectors"]


content_handler = ContentHandler()

credentials_profile_name = (
    "gws"
)
embeddings = SagemakerEndpointEmbeddings(
    # endpoint_name="endpoint-name",
    # credentials_profile_name="credentials-profile-name",
    endpoint_name="annil-chat-glm-6b-v2",
    region_name="ap-southeast-1",
    content_handler=content_handler,
    credentials_profile_name=credentials_profile_name
)

query_result = embeddings.embed_query("foo")

doc_results = embeddings.embed_documents(["foo"])

doc_results
