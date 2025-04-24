import getpass
import os
import tools

from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from langchain.load import dump
from vector_store import vector_store

os.environ["TOKENIZERS_PARALLELISM"] = "false"
if not os.environ.get("DEEPSEEK_API_KEY"):
  os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter API key for Deepseek: ")


class AgentInvestor:
    def __init__(self, llm, debug=False):
        self.llm = llm
        self.debug = debug
        self.system = """你是一个投资者，回答提问者关于投资方面的问题。每个回答都要总结提问者输入的事实，调用工具 save_fact 来保存用户输入的事实。每个回答都必须调用工具 query_clickhouse"""

        self.prompt = ChatPromptTemplate(
            [
                ("system", self.system),
                ("human", "已知: {doc_from_vector} 请问 {query}"),
            ]
        )
        self.add_tools()

    def add_tools(self):
        self.tools = tools.all_tools
        self.model_with_tools = self.llm.bind_tools(self.tools)
        self.chain = self.prompt | self.model_with_tools

    def query(self, query):
        print("start query: ", query)
        doc_from_vector = vector_store.query(query)
        doc_from_vector_str = "\n".join(map(lambda x: x.page_content, doc_from_vector))
        if self.debug:
            print("get doc from vector", doc_from_vector_str)

        ai_msg = self.chain.invoke({"query": query, "doc_from_vector": doc_from_vector_str})
        if self.debug:
            print("ai_msg.content:", ai_msg.content)
            print("ai_msg.tool_calls:", ai_msg.tool_calls)

        messages = [query]
        messages.append(ai_msg.content)

        for tool_call in ai_msg.tool_calls:
            selected_tool = list(filter(lambda x: x.name == tool_call["name"], self.tools))[0]
            tool_msg = selected_tool.invoke(tool_call)
            messages.append(tool_msg)
            tool_msg.pretty_print()

        if self.debug:
            print(dump.dumps(messages, ensure_ascii=False, pretty=True))

    def query_test(self, query):
        print(query)

    def loop(self):
        while True:
            lines = []
            first_line = True
            while True:
                if first_line:
                    print("\n\n===== 输入 end 结束输入, quit 退出 =====\n>> ", end='', flush=True)
                    first_line = False
                line = input().strip()
                if line == 'quit':
                    print("程序退出。")
                    exit()
                if line == 'end':
                    break
                lines.append(line)
            if lines:
                multiline_text = '\n'.join(lines)
                self.query(multiline_text)


if __name__ == "__main__":
    llm_deepseek = ChatDeepSeek(
        model="deepseek-chat",
        # model="deepseek-reasoner",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    agent = AgentInvestor(llm_deepseek, debug=False)
    agent.loop()
    # agent.query("""请编写 SQL 查询2024年最后一个季度各个机构分别的持仓金额，按照持仓市值倒排序，最多20条""")

#     agent.query("""已知：Clickhouse 数据中的 inv.F13 表，里面存放各个机构在各个季度的美股持仓数据，每个机构每个季度都会上报一次完整的持仓，多个季度的持仓不能累加。REPORT_DATE 数据所覆盖的季度，格式为 2014-09-30，每年共 4 个季度上报，对应于 一季度 03-31、二季度 06-30、三季度 09-30、 和四季度 12-31。
# 已知：inv.F13 建表语句为：create table inv.F13 ( ACCESSION_NUMBER String COMMENT "提交编号, 每次机构提交都有唯一的编号",
#     INFOTABLE_SK Int64,
#     NAMEOFISSUER String COMMENT "持仓标的，股票名称，被持仓的公司",
#     TITLEOFCLASS String,
#     CUSIP String,
#     FIGI String,
#     VALUE Int64 COMMENT "持仓市值，单位美金",
#     SSHPRNAMT Int64 COMMENT "持仓股数",
#     SSHPRNAMTTYPE String,
#     PUTCALL String,
#     INVESTMENTDISCRETION String,
#     OTHERMANAGER String,
#     VOTING_AUTH_SOLE String,
#     VOTING_AUTH_SHARED String,
#     VOTING_AUTH_NONE String,
#     FILING_DATE	 String,
#     SUBMISSIONTYPE String,
#     CIK String COMMENT "持仓机构 CIK 编号",
#     PERIODOFREPORT String,
#     FILINGMANAGER_NAME String COMMENT "持仓机构名字",
#     FILINGMANAGER_CITY String COMMENT "持仓机构所在的地址",
#     REPORT_DATE String COMMENT "对应的季度，格式为 2014-09-30，每年共 4 个季度上报，对应于 一季度 03-31、二季度 06-30、三季度 09-30、 和四季度 12-31"
# ) ENGINE = MergeTree()
# ORDER BY (REPORT_DATE, CIK);
#
# 请编写 SQL 查询2024年最后一个季度各个机构分别的持仓金额，按照持仓市值倒排序，最多20条
#     """)

