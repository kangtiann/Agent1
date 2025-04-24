import getpass
import os

from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.load import dump
from langchain_core.output_parsers import StrOutputParser

if not os.environ.get("DEEPSEEK_API_KEY"):
  os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter API key for Deepseek: ")

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


llm = ChatDeepSeek(
    model="deepseek-chat",
    # model="deepseek-reasoner",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

tools = [list_files_in_dir, multiply]
# Tool binding
model_with_tools = llm.bind_tools(tools)

# prompt = ChatPromptTemplate(
#     [
#         (
#             "system",
#             "You are a helpful assistant that translates {input_language} to {output_language}.",
#         ),
#         ("human", "{input}"),
#     ]
# )
#
# chain = prompt | llm
# result = chain.invoke(
#     {
#         "input_language": "English",
#         "output_language": "Chinese",
#         "input": "I love programming, Hello world.",
#     }
# )
#
# print(result.content)

prompt = ChatPromptTemplate(
    [
        (
            "system",
            "You are a helpful assistant, you should do work for user asked",
        ),
        ("human", "{input}"),
    ]
)

query = "3 乘以 12 是多少？列出 /Users 目录下有哪些文件"

messages = [query]

ai_msg = model_with_tools.invoke(query)
print((prompt | model_with_tools).invoke({"input": query}))
# print(ai_msg.tool_calls)
#
# for tool_call in ai_msg.tool_calls:
#     selected_tool = list(filter(lambda x: x.name == tool_call["name"], tools))[0]
#     tool_msg = selected_tool.invoke(tool_call)
#     messages.append(tool_msg)
#
# print(dump.dumps(messages, ensure_ascii=False, pretty=True))


