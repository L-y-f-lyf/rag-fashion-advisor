import datetime
import  os
from langchain_community.embeddings import DashScopeEmbeddings
import config_data
import config_data  as  config
import hashlib
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

def check_md5(md5_str :str):
    """检查传入的MD5是否已经被处理过"""
    if not os.path.exists(config.md5_path):
        """文件存不存在"""
        open(config.md5_path, 'w' ,encoding='utf-8').close()
        return False
    else:
        for line in open(config.md5_path, 'r' ,encoding='utf-8').readlines():
            line =line.strip()
            if line == md5_str:
                return True
        return False
def save_md5(md5_str :str):
    """将传入的MD5字符串。记录到文件内保存"""
    with open(config.md5_path, 'a' ,encoding='utf-8') as f:
        f.write(md5_str + '\n')



def get_string_md5(input_str :str, encoding='utf-8'):
    """将传入的字符串转换为MD5字符串"""

    """将字符串转换为bytres字节数组"""
    str_bytes = input_str.encode(encoding=encoding)
    md5_obj = hashlib.md5() #得到MD5对象
    md5_obj.update(str_bytes) #更新内容
    md5_hex = md5_obj.hexdigest()  #得到MD5的十六进制字符串
    return md5_hex


class knowledgeBaseService(object):
    # 基础服务
    def __init__(self):
        # 如果文件夹不存在则创建
        os.makedirs(config.persist_directory, exist_ok=True)
        self.chroma = Chroma(

            collection_name = config.collections_name,   #数据库的表名
            embedding_function = DashScopeEmbeddings(
                model="text-embedding-v4",
                dashscope_api_key=config_data.dashscope_api_key

        ),
            persist_directory =config.persist_directory,   #数据库本地文件夹

        )
        self.spliter =RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,#分割后的文本段最大长度
            chunk_overlap=config.chunk_overlap,#连续文本段之间的字符重叠数量
            separators=config.separators,#自然段落划分的符号
            length_function=len,#len函数做长度统计

        )

    def upload_by_str(self,data : str,filename):
        """将传入的字符串进行向量化存入"""

        md5_hex = get_string_md5(data)

        if check_md5(md5_hex):
            return  "[跳过]内容已经传入数据库中"

        if len(data) > config.max_split_char_number:#分割
            knowledge_chunks : list[str]=self.spliter.split_text(data)
        else:
            knowledge_chunks= [data]#保证数据类型都是列表

        metadata ={
            "source": filename,
            "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator":"梁亚飞"
        }

        self.chroma.add_texts(
            # 存入向量库
            knowledge_chunks,
            metadatas =[metadata for _ in knowledge_chunks],
        )
        save_md5(md5_hex)

        return  "[成功]内容已经成功载入向量库"


if __name__ == '__main__':
    # # r1 = get_string_md5("梁亚飞")
    # save_md5("20d9e7685d295e6e449b9e6f502411da")
    # print(check_md5("20d9e7685d295e6e449b9e6f502411da"))
    # # print(r1)
    service = knowledgeBaseService()
    r = service.upload_by_str("梁亚辉","textfile")
    print(r)




