# -*- coding: utf-8 -*-
# Name：孙圣雷
# Time：2024/7/28 下午9:28
import ctypes
import errno
import gc
import os
import shutil
import subprocess
import sys

import psutil

from my_llm import llm
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader,PyPDFium2Loader,CSVLoader,Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

embeddings = HuggingFaceEmbeddings(
    model_name="GanymedeNil/text2vec-large-chinese", cache_folder="./text2vec-large-chinese"
)


def create_chroma_db(db_name, temp_source_file_path):
    persist_directory = "./dbs/" + db_name
    os.mkdir("./can_get_dbs/" + db_name)
    extension = temp_source_file_path.split(".")[-1]
    loader = None
    if extension == 'txt':
        loader = TextLoader(temp_source_file_path,encoding='utf8')
    if extension == 'pdf':
        loader = PyPDFium2Loader(temp_source_file_path)
    if extension == 'docx':
        loader = Docx2txtLoader(temp_source_file_path)

    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=persist_directory)

    try:
        os.remove(temp_source_file_path)
    except Exception as e:
        print(f"Error deleting temporary file: {e}")

    return "ok"


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def answer_user_query(db_name, question):
    persist_directory = "./dbs/" + db_name
    vectorstore = Chroma(embedding_function=embeddings, persist_directory=persist_directory)

    retriever = vectorstore.as_retriever()

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "先判断一下用户的问题和参考内容是否有关，如果有关，则结合参考内容进行回答，如果无关，则请你像买看见参考内容一样即可。即若是user的问题和参考内容无关，则不要回答参考内容相关的信息，问题和参考内容是否有关系对用户来说是不可感知的\n##强调：你不要在回答中画蛇添足"),
            ("user", "我的问题是:{question}，\n可参考以下内容：{context}")
        ]
    )

    return llm.stream(prompt_template.invoke(
        {"context": format_docs(retriever.invoke(question)), "question": question}
    ).to_messages())



def delete_chroma_db(db_name):
    persist_directory = "./can_get_dbs/" + db_name

    try:
        if os.path.exists(persist_directory):
            shutil.rmtree(persist_directory, ignore_errors=True)
            print(f"成功强制删除目录:  {persist_directory}")
        else:
            print(f"目录  {persist_directory}  不存在")
    except  Exception as e:
        print(f"强制删除目录时出错:  {e}")
    return "ok"

def get_all_segments(db_name):
    persist_directory = "./dbs/" + db_name
    vectorstore = Chroma(embedding_function=embeddings, persist_directory=persist_directory)
    res = vectorstore.get()
    return res

def delete_segments_by_id(db_name,id):
    persist_directory = "./dbs/" + db_name
    vectorstore = Chroma(embedding_function=embeddings, persist_directory=persist_directory)
    print(vectorstore.delete(ids=[id]))
    return "ok"

def update_segments_by_id(db_name,id,new_content,metedata_source):
    persist_directory = "./dbs/" + db_name
    vectorstore = Chroma(embedding_function=embeddings, persist_directory=persist_directory)
    print(vectorstore.update_document(document_id=id,document=Document(page_content=new_content,metadata={"source": metedata_source})))
    return "ok"

def add_new_segments(db_name,new_content,metadata_source):
    persist_directory = "./dbs/" + db_name
    vectorstore = Chroma(embedding_function=embeddings, persist_directory=persist_directory)
    return vectorstore.add_documents(documents=[Document(page_content=new_content,metadata={"source": metadata_source})])

def add_new_context(folder_path, db_name, batch_size=10):
    """ 🐳🐳🐳
    :param folder_path: news folder path
    :param db_name: from web
    :param batch_size: optimize the size of documents
    :return: json
    """

    persist_directory = os.path.join("./dbs", db_name)

    if not os.path.exists(persist_directory):
        try:
            os.makedirs(persist_directory)
            print(f"Directory created: {persist_directory}")
        except OSError as e:
            print(f"Error creating directory {persist_directory}: {e}")
            return "error"

    try:
        vectorstore = Chroma(embedding_function=embeddings, persist_directory=persist_directory)
        """ print(vectorstore.get()) """
    except Exception as e:
        print(f"Error initializing vectorstore: {e}")
        return "error"

    try:
        file_list = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

        def extract_number(filename):
            try:
                return int(filename.split('.')[0])
            except ValueError:
                return float('inf')

        file_list.sort(key=extract_number)
    except Exception as e:
        print(f"Error listing or sorting files in {folder_path}: {e}")
        return "error"

    max_files = 20
    file_list = file_list[:max_files]

    for i in range(0, len(file_list), batch_size):
        batch_files = file_list[i:i + batch_size]
        for filename in batch_files:
            temp_source_file_path = os.path.join(folder_path, filename)
            print(f"Processing file: {temp_source_file_path}")
            try:
                loader = PyPDFium2Loader(temp_source_file_path)
                docs = loader.load()

                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                splits = text_splitter.split_documents(docs)

                vectorstore.add_documents(documents=splits)
                print("Document added to vectorstore.")

                process = psutil.Process(os.getpid())
                mem_info = process.memory_info()

                print(f"当前进程使用的内存: {mem_info.rss / (1024 * 1024)} MB")
                try:
                    os.remove(temp_source_file_path)
                    print(f"Deleted file: {temp_source_file_path}")
                except Exception as e:
                    print(f"Error deleting temporary file: {e}")

            except Exception as e:
                print(f"Error processing file {temp_source_file_path}: {e}")
                continue

        gc.collect()
    try:
        vectorstore.persist()
        print("Database updated and saved.")
    except Exception as e:
        print(f"Error persisting vectorstore: {e}")
        return "error"
    return "ok"

if __name__ == "__main__":
    folder_path = "news"
    db_name = "test4.0"
    temp_source_file_path = "D:\\SmartReportv1.0\\news\\2.pdf"
    """
       报错：
            进程已结束，退出代码为 -1073741819 (0xC0000005)
       原因排查：
            ❗内存泄露 -1073741819 (0xC0000005) 🐳🐳🐳 ✔️✔️✔️ 
            ❗权限问题 -1073741819 (0xC0000005) 🐳🐳🐳 ✖️✖️✖️
    """

    # create_chroma_db(db_name, temp_source_file_path)
    # add_new_context(folder_path, db_name)
    # print(get_all_segments(db_name))
    # add_new_segments(db_name, "你好", "1111")
    print(get_all_segments(db_name))

""" V1.1 (内存过小，无法添加文档) 🐳🐳🐳
def add_new_context(folder_path, db_name):
    persist_directory = os.path.join("./dbs", db_name)

    if not os.path.exists(persist_directory):
        try:
            os.makedirs(persist_directory)
            print(f"Directory created: {persist_directory}")
        except OSError as e:
            print(f"Error creating directory {persist_directory}: {e}")
            return "error"

    try:
        vectorstore = Chroma(embedding_function=embeddings, persist_directory=persist_directory)
        print(vectorstore.get())
    except Exception as e:
        print(f"Error initializing vectorstore: {e}")
        return "error"

    try:
        file_list = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

        def extract_number(filename):
            try:
                return int(filename.split('.')[0])
            except ValueError:
                return float('inf')

        file_list.sort(key=extract_number)
    except Exception as e:
        print(f"Error listing or sorting files in {folder_path}: {e}")
        return "error"

    for filename in file_list:
        temp_source_file_path = os.path.join(folder_path, filename)
        print(f"Processing file: {temp_source_file_path}")

        try:
            loader = TextLoader(temp_source_file_path, encoding='utf8')
            docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)

            vectorstore.add_documents(documents=splits)

            gc.collect()
            print("Document added to vectorstore.")

        except Exception as e:
            print(f"Error processing file {temp_source_file_path}: {e}")
            continue

        try:
            os.remove(temp_source_file_path)
        except Exception as e:
            print(f"Error deleting temporary file: {e}")

    try:
        vectorstore.persist()
        print("Database updated and saved.")
    except Exception as e:
        print(f"Error persisting vectorstore: {e}")
        return "error"

    return "ok"  
"""


""" V1.0 (文件读入错误) 🐳🐳🐳
def add_chroma_db(db_name, temp_source_file_path):
    persist_directory = "./dbs/" + db_name
    os.makedirs(persist_directory, exist_ok=True)

    extension = temp_source_file_path.split(".")[-1]
    loader = None
    if extension == 'txt':
        loader = TextLoader(temp_source_file_path, encoding='utf8')
    elif extension == 'pdf':
        loader = PyPDFium2Loader(temp_source_file_path)
    elif extension == 'docx':
        loader = Docx2txtLoader(temp_source_file_path)
    else:
        raise ValueError("Unsupported file extension: {}".format(extension))

    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=persist_directory)

    try:
        os.remove(temp_source_file_path)
    except Exception as e:
        print(f"Error deleting temporary file: {e}")

    return "ok"
"""