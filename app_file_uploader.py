import streamlit as st
from knowledge_base import knowledgeBaseService


st.title("知识库更新服务")

uploader_file=st.file_uploader(
    "请上传txt文件",
    type=['TXT'],
    accept_multiple_files=False,
)

if "service" not in st.session_state:
    st.session_state["service"]= knowledgeBaseService()



if uploader_file is not None:
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size/1024
    st.subheader(f"文件名 ； {file_name}")
    st.write(f"格式：{file_type} |大小: {file_size}")
    text = uploader_file.getvalue().decode("utf-8")
    result = st.session_state["service"].upload_by_str(text,file_name)
    st.write(result)


