import requests
from bs4 import BeautifulSoup
import pandas as pd
from lxml import etree
import xml.etree.ElementTree as ET
import time
import re
from io import StringIO


# 伯克希尔的SEC CIK编号（固定值）
BERKSHIRE_CIK = "0001067983"

def fetch_13f_filings(cik):
    """
    获取伯克希尔哈撒韦的13F文件列表
    """
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=13F&dateb=&owner=exclude&count=100"
    headers = {"User-Agent": "Your Name (your.email@example.com)"}  # 必须填写合规的User-Agent

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    filings = []

    # 解析所有13F文件链接
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) > 1 and "13F-HR" in cells[0].text:
            filing_date = cells[3].text.strip()
            filing_link = "https://www.sec.gov" + cells[1].a["href"]
            filings.append({"date": filing_date, "url": filing_link})

    return filings


def parse_13f_document(document_url):
    """
    解析13F文档中的持仓表格
    """
    headers = {"User-Agent": "Your Name (your.email@example.com)"}
    response = requests.get(document_url, headers=headers)

    # 提取XML格式的持仓数据（SEC使用XML格式存储结构化数据）
    if "xml" in response.text:
        # 去除 xmlns 信息，不然索引不出来
        content = re.sub(' xmlns="[^"]+"', '', response.text, count=1)
        tree = ET.parse(StringIO(content))
        holdings = []
        for entry in tree.getroot():
            data = {
                "issuer": entry.find("nameOfIssuer").text,
                "value": entry.find("value").text,
                "shares": entry.find("shrsOrPrnAmt/sshPrnamt").text,
                "title": entry.find("titleOfClass").text,
                "cusip": entry.find("cusip").text
            }
            holdings.append(data)
        return pd.DataFrame(holdings)
    else:
        print("非结构化文档（HTML/TXT），需手动解析")
        return None


# 示例调用
if __name__ == "__main__":
    # 步骤1：获取所有13F文件列表
    filings = fetch_13f_filings(BERKSHIRE_CIK)
    print(f"找到 {len(filings)} 份13F报告")

    # 步骤2：下载并解析最新一份13F报告
    latest_filing = filings[0]
    print(f"解析报告日期：{latest_filing['date']}")

    # 获取文档详情页（找到实际的.txt或.xml文件链接）
    print("latest_filing", latest_filing["url"])
    doc_response = requests.get(latest_filing["url"], headers={"User-Agent": "TianXiaokang masterkang163@163@163.com"})
    doc_soup = BeautifulSoup(doc_response.text, "html.parser")
    doc_link = "https://www.sec.gov" + doc_soup.find("a", string=lambda t: t and re.match("^\\d+.xml", t))["href"]
    print("doc_link", doc_link)

    # 步骤3：解析持仓数据
    df = parse_13f_document(doc_link)
    print(df)
    if df is not None:
        df.to_csv("berkshire_13f_holdings.csv", index=False)
        print("持仓数据已保存为 CSV 文件")
