import getpass
import os
from langchain_core.output_parsers import StrOutputParser

from fragments.reddit import Reddit

from langchain_deepseek import ChatDeepSeek

if not os.environ.get("DEEPSEEK_API_KEY"):
  os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter API key for Deepseek: ")


llm = ChatDeepSeek(
    model="deepseek-chat",
    # model="deepseek-reasoner",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)
parser = StrOutputParser()

resp = llm.invoke("所有指环王电影的总运行时长是多久?")
parsed_text = parser.invoke(resp)
print(parsed_text)  # 输出纯字符串



