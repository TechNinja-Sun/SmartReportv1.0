# -*- coding: utf-8 -*-
# Name：孙圣雷
# Time：2024/8/2 下午8:42
from flask import Flask, request, jsonify, render_template, send_file, stream_with_context
import time
import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from markdown2 import markdown
import logging
import sys
from db_operation import (
    create_chroma_db as create_db,
    answer_user_query,
    delete_chroma_db as delete_db,
    get_all_segments as get_all,
    delete_segments_by_id,
    update_segments_by_id,
    add_new_context,
)
from add_knowledge import (
    _add_knowledge
)

# logging.basicConfig(
#     filename='error_log.txt',
#     level=logging.ERROR,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

app = Flask(__name__)

def ensure_dir(f):
    dir = os.path.dirname(f)
    if not os.path.exists(dir):
        os.makedirs(dir)
#
# def log_error(exc_type, exc_value, exc_traceback):
#     logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
#
# sys.excepthook = log_error

@app.route("/create_chroma_db", methods=['POST', 'GET'])
def create_chroma_db():
    db_name = request.form['db_name']
    source_file = request.files['source']
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    source_file_temp_save_path = f"{timestamp}_{source_file.filename}"

    basedir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(basedir, 'uploads', source_file_temp_save_path)

    ensure_dir(filepath)
    source_file.save(filepath)

    result = create_db(db_name, filepath)
    return jsonify({"message": result})

@app.route("/knowledge_list", methods=['POST', 'GET'])
def knowledge_list():
    directory_path = 'can_get_dbs'
    entries = os.listdir(directory_path)
    subdirectories = [d for d in entries if os.path.isdir(os.path.join(directory_path, d))]
    return jsonify(subdirectories)

# @app.route("/query", methods=['POST'])
# def query():
#     db_name = request.form['db_name']
#     question = request.form['question']
#
#     def generate_chunks():
#         for chunk in answer_user_query(db_name=db_name, question=question):
#             yield chunk.content
#
#     return stream_with_context(generate_chunks())

@app.route("/query", methods=['POST'])
def query():
    db_name = request.form['db_name']
    question = request.form['question']

    summary_content = generate_summary(db_name, question)

    pdf = create_pdf(summary_content)

    return send_file(io.BytesIO(pdf), mimetype='application/pdf', as_attachment=True, download_name="summary.pdf")

def generate_summary(db_name, question):
    content = ""
    for chunk in answer_user_query(db_name=db_name, question=question):
        content += chunk.content
    return content

# def create_pdf(content):
#     buffer = io.BytesIO()
#     c = canvas.Canvas(buffer, pagesize=letter)
#     textobject = c.beginText(100, 750)
#     textobject.setTextOrigin(100, 750)
#     textobject.textLines(content)
#     c.drawText(textobject)
#     c.save()
#     buffer.seek(0)
#     return buffer.getvalue()

def create_pdf(content):
    html_content = markdown(content)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))

    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'SimHei'

    story = []
    for line in html_content.split('\n'):
        story.append(Paragraph(line, styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

@app.route("/delete_chroma_db", methods=['POST'])
def delete_chroma_db():
    db_name = request.form['db_name']
    result = delete_db(db_name)
    return jsonify({"message": result})

@app.route("/get_all_segments", methods=['POST'])
def get_all_segments():
    db_name = request.form['db_name']
    segments = get_all(db_name)
    return jsonify(segments)

@app.route("/delete_segments_by_id", methods=['POST'])
def _delete_segments_by_id():
    db_name = request.form['db_name']
    segment_id = request.form['id']
    delete_segments_by_id(db_name, segment_id)
    return jsonify({"message": "段落已删除"})

@app.route("/update_segments_by_id", methods=['POST'])
def _update_segments_by_id():
    db_name = request.form['db_name']
    segment_id = request.form['id']
    new_content = request.form['new_content']
    metadata_source = request.form['metedata_source']

    result = update_segments_by_id(db_name, segment_id, new_content, metadata_source)
    return jsonify({"message": result})

# @app.route("/addContent", methods=['POST'])
# def _add_new_segments():
#     db_name = request.form['db_name']
#     new_content = add_knowledge(request.form['web_path'])
#     metadata_source = request.form['metedata_source']
#
#     result = add_new_segments(db_name, new_content, metadata_source)
#     return jsonify({"message": result})


#
# @app.route("/addContent", methods=['POST'])
# def _add_new_segments():
#     data = request.get_json()
#     db_name = data.get('db_name')
#     web_path = data.get('web_path')
#     # print(web_path)
#     new_content = _add_knowledge(web_path)
#
#     if not db_name or not new_content:
#         return jsonify({"error": "缺少必要字段: db_name 和 web_path"}), 400
#
#     metadata_source = data.get('metedata_source', '')
#
#     result = add_new_segments(db_name, new_content, metadata_source)
#     return jsonify({"message": result})

@app.route("/addContent", methods=['POST'])
def _add_new_segments():
    data = request.get_json()
    db_name = data.get('db_name')
    web_path = data.get('web_path')
    _add_knowledge(web_path)

    folder_path = "D:/SmartReportv1.0/news"
    add_new_context(folder_path,db_name)

    return jsonify({"message": "内容添加成功"})



@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)







# from flask import Flask, request, jsonify, render_template
# import time
# import os
# from flask import stream_with_context
# from db_operation import (
#     create_chroma_db as create_db,
#     answer_user_query,
#     delete_chroma_db as delete_db,
#     get_all_segments as get_all,
#     delete_segments_by_id,
#     update_segments_by_id,
#     add_new_segments
# )
# from uploads import add_knowledge
#
# app = Flask(__name__)
#
#
# def ensure_dir(f):
#     dir = os.path.dirname(f)
#     if not os.path.exists(dir):
#         os.makedirs(dir)
#
#
# @app.route("/create_chroma_db", methods=['POST', 'GET'])
# def create_chroma_db():
#     db_name = request.form['db_name']
#     source_file = request.files['source']
#     source_file_temp_save_path = str(time.time()) + "_" + source_file.filename
#
#     basedir = os.path.abspath(os.path.dirname(__file__))  # 当前文件夹路径
#     filepath = os.path.join(basedir, 'uploads', source_file_temp_save_path)  # uploads是存放文件的子目录
#
#     ensure_dir(filepath)
#     source_file.save(filepath)
#
#     result = create_db(db_name, filepath)
#     return jsonify({"message": result})
#
#
# @app.route("/knowledge_list", methods=['POST', 'GET'])
# def knowledge_list():
#     directory_path = 'can_get_dbs'
#     entries = os.listdir(directory_path)
#     subdirectories = [d for d in entries if os.path.isdir(os.path.join(directory_path, d))]
#     return jsonify(subdirectories)
#
# @app.route("/query", methods=['POST'])
# def query():
#     db_name = request.form['db_name']
#     question = request.form['question']
#
#     def generate_chunks():
#         for chunk in answer_user_query(db_name=db_name, question=question):
#             yield chunk.content
#
#     return stream_with_context(generate_chunks())
#
#
# @app.route("/delete_chroma_db", methods=['POST'])
# def delete_chroma_db():
#     db_name = request.form['db_name']
#     result = delete_db(db_name)
#     return jsonify({"message": result})
#
#
# @app.route("/get_all_segments", methods=['POST'])
# def get_all_segments():
#     db_name = request.form['db_name']
#     segments = get_all(db_name)
#     return jsonify(segments)
#
#
# @app.route("/delete_segments_by_id", methods=['POST'])
# def _delete_segments_by_id():
#     db_name = request.form['db_name']
#     segment_id = request.form['id']
#     delete_segments_by_id(db_name, segment_id)
#     return jsonify({"message": "段落已删除"})
#
#
# @app.route("/update_segments_by_id", methods=['POST'])
# def _update_segments_by_id():
#     db_name = request.form['db_name']
#     segment_id = request.form['id']
#     new_content = request.form['new_content']
#     metadata_source = request.form['metedata_source']
#
#     result = update_segments_by_id(db_name, segment_id, new_content, metadata_source)
#     return jsonify({"message": result})
#
# @app.route("/addContent", methods=['POST'])
# def _add_new_segments():
#     db_name = request.form['db_name']
#     new_content = add_knowledge(request.form['web_path'])
#     metadata_source = request.form['metedata_source']
#
#     result = add_new_segments(db_name, new_content, metadata_source)
#     return jsonify({"message": result})
#
# @app.route("/", methods=['GET'])
# def index():
#     return render_template('index.html')
#
# # @app.route("/create_db", methods=['GET'])
# # def create_db_page():
# #     return render_template('create_db.html')
# #
# # @app.route("/query", methods=['GET'])
# # def query_page():
# #     return render_template('query.html')
# #
# # @app.route("/manage_db", methods=['GET'])
# # def manage_db_page():
# #     return render_template('manage_db.html')
# #
# # @app.route("/all_segments", methods=['GET'])
# # def all_segments_page():
# #     return render_template('all_segments.html')
#
# if __name__ == "__main__":
#     app.run(debug=True)
