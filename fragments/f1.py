import getpass
import os

from langchain_deepseek import ChatDeepSeek

from pydantic import BaseModel, Field
class ResponseFormatter(BaseModel):
    """Always use this tool to structure your response to the user."""
    answer: str = Field(description="The answer to the user's question")
    followup_question: str = Field(description="A followup question the user could ask")


if not os.environ.get("DEEPSEEK_API_KEY"):
  os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter API key for Deepseek: ")

from langchain.chat_models import init_chat_model

# model = init_chat_model("deepseek-reasoner", model_provider="deepseek")
#
# ouput = model.invoke("学习数论的路径是什么？相关书籍请引用英文书籍")
# print(ouput)


# schema = {"market_value": "Market value"}
# model1 = model.with_structured_output(schema)
# ouput = model1.invoke("英伟达市值是多少？用美元为单位")
# print("英伟达市值为（美元）："+ouput["market_value"])
#

model = ChatDeepSeek(model="deepseek-reasoner")
ai_msg = model.invoke("Return a JSON object with key 'random_ints' and a value of 10 random ints in [0-99]")
print(ai_msg.content)

#
# ouput = model.with_structured_output({"market_value": "Market value"}).invoke("英伟达市值是多少？用人民币为单位")
# print("英伟达市值为（人民币）："+ouput["market_value"])
#
#
