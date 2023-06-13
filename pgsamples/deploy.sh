#!/bin/bash

cd ..
pip install ".[pgsamples]"
cd pgsamples
streamlit run app.py chatglm