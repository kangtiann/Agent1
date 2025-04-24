import os
import clickhouse_connect
from langchain_core.tools import tool
from vector_store import vector_store
import traceback

ck_client = clickhouse_connect.get_client(host='localhost', username='agent')


@tool
def list_files_in_dir(path: str) -> str:
    """list files in a dir, 列出文件夹下面有哪些文件"""
    return "\n".join(os.listdir(path))


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers.

    Args:
        a: First integer
        b: Second integer
    """
    return a * b * 2


@tool
def query_clickhouse(sql: str) -> str:
    """SQL、查询SQL、查询 ClickHouse、分析、分析持仓、查询本地 Clickhouse 数据库, 可以执行类似下面任务：查询机构持仓、查询上市公司的股票信息、机构持仓分析，如 伯克希尔、贝莱德、先锋领航等

    参数:
    sql: 查询的 SQL 语句

    返回值：查询结果，为 String 类型
    """
    print("will exec SQL: ", sql)
    try:
        df = ck_client.query_df(sql)
        result = str(df)
        ck_client.close()
        return result
    except clickhouse_connect.driver.exceptions.DatabaseError:
        traceback.print_stack()
    return "[ERROR] query clickhouse error"


@tool
def save_vectordb(text: str) -> str:
    """保存到向量数据库的文本

    参数:
    text: 文本

    返回值：保存结果
    """
    if text:
        vector_store.save_doc(text)
        return "已保存"
    return "无需保存"


@tool
def save_fact(fact: str) -> str:
    """已知，事实，保存用户输入的事实信息

    参数:
    fact: 输入的事实/已知信息

    返回值：保存结果
    """
    if fact:
        saved = vector_store.save_doc(fact)
        if saved:
            return "学习到的新知识已保存: " + fact
        else:
            return "没有新知识需要保存"
    return "没有新知识需要保存"


all_tools = [save_vectordb,
             save_fact,
             query_clickhouse,
             list_files_in_dir,
             multiply]
