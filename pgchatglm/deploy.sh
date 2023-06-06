#!/bin/bash

export ENDPOINT_NAME=annil-chat-glm-6b-v2

cd ..
pip install ".[pgchatglm]"
cd pgchatglm
streamlit run app.py chatapp