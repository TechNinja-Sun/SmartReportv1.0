# -*- coding: utf-8 -*-
# Name：孙圣雷
# Time：2024/7/14 上午9:18
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-97056e0eb2dd493aae8a453ad2b54ad8",
    model='qwen2-72b-instruct',
    temperature=0,
)

