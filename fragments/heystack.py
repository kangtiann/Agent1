from haystack.utils import Secret
from haystack.components.agents import Agent
from haystack.tools.component_tool import ComponentTool
from haystack.components.websearch import SerperDevWebSearch
from haystack.dataclasses import Document, ChatMessage
from haystack.components.generators.chat import OpenAIChatGenerator
from typing import List

llm = OpenAIChatGenerator(
    model="deepseek-chat",
    api_base_url="https://api.deepseek.com/v1",
    api_key=Secret.from_env_var("DEEPSEEK_API_KEY"))

# Create the web search component
web_search = SerperDevWebSearch(top_k=3)

# Create the ComponentTool with simpler parameters
web_tool = ComponentTool(
    component=web_search,
    name="web_search",
    description="Search the web for current information like weather, news, or facts."
)

# Create the agent with the web tool
tool_calling_agent = Agent(
    chat_generator=llm,
    system_prompt="""You're a helpful agent. When asked about current information like weather, news, or facts, 
                     use the web_search tool to find the information and then summarize the findings.
                     When you get web search results, extract the relevant information and present it in a clear, 
                     concise manner.""",
    tools=[web_tool]
)

# Run the agent with the user message
user_message = ChatMessage.from_user("请到 https://edition.cnn.com/markets/fear-and-greed 页面查询 Fear & Greed Index 值")
result = tool_calling_agent.run(messages=[user_message])

# Print the result - using .text instead of .content
print(result["messages"][-1].text)
