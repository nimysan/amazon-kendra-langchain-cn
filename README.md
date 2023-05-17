# Amazon Kendra + ChatGLM on SageMaker 进行中文增强搜索

## 英文增强搜索方案请参考以下链接：
https://aws.amazon.com/cn/blogs/machine-learning/quickly-build-high-accuracy-generative-ai-applications-on-enterprise-data-using-amazon-kendra-langchain-and-large-language-models/

## Installing

Clone the repository
```bash
git clone https://github.com/micxyj/amazon-kendra-langchain-cn.git
```

Move to the repo dir
```bash
cd amazon-kendra-langchain-cn
```

Install the dependencies
```bash
pip install boto3
pip install langchain
pip install streamlit
```

Install the classes
```bash
pip install .
```

## Usage

## Creating an Amazon Kendra index and data source
https://docs.aws.amazon.com/kendra/latest/dg/what-is-kendra.html

## Deploy ChatGLM on SageMaker
https://catalog.us-east-1.prod.workshops.aws/workshops/1ac668b1-dbd3-4b45-bf0a-5bc36138fcf1/zh-CN/3-configuration-llm/3-1-chatglm

## Running samples
For executing sample chains, install the optional dependencies
```bash
pip install ".[samples]"
```

### Configure AWS credential
https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html

### Configure env
Ensure that the environment variables are set for the aws region, kendra index id and the provider/model used by the sample.
For example, for running the `kendra_chatGLM.py` sample, these environment variables must be set: AWS_REGION, KENDRA_INDEX_ID
and CHATGLM_ENDPOINT.
You can use commands as below to set the environment variables.
```bash
export AWS_REGION="<YOUR-AWS-REGION>"
export KENDRA_INDEX_ID="<YOUR-KENDRA-INDEX-ID>"
export CHATGLM_ENDPOINT="<YOUR-SAGEMAKER-ENDPOINT-FOR-CHATGLM>"
```

### Running samples from the streamlit app
The samples directory is bundled with an `app.py` file that can be run as a web app using streamlit.
```bash
cd samples
streamlit run app.py chatglm
```

### Running samples from the command line
```bash
python samples/<sample-file-name.py>
```

## Uninstall
```bash
pip uninstall aws-langchain
```
