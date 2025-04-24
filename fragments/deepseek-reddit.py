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

reddit = Reddit()
posts = reddit.get_last_posts("wallstreetbets", limit=10)
print("finish posts, num: ", len(posts))
resp = llm.invoke("请帮我列出下面提及最多美股股票代码及公司简介，用中文回答。 " + "\n".join(posts))
parsed_text = parser.invoke(resp)
print(parsed_text)  # 输出纯字符串



