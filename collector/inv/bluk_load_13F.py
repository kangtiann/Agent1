import os
import pandas as pd
from datetime import datetime

"""
create database inv;
use inv;

create table inv.F13 (
    ACCESSION_NUMBER String COMMENT "提交编号, 每次机构提交都有唯一的编号",
    INFOTABLE_SK Int64,
    NAMEOFISSUER String COMMENT "持仓标的，股票名称，被持仓的公司",
    TITLEOFCLASS String,
    CUSIP String,
    FIGI String,
    VALUE Int64 COMMENT "持仓市值，单位美金",
    SSHPRNAMT Int64 COMMENT "持仓股数",
    SSHPRNAMTTYPE String,
    PUTCALL String,
    INVESTMENTDISCRETION String,
    OTHERMANAGER String,
    VOTING_AUTH_SOLE String,
    VOTING_AUTH_SHARED String,
    VOTING_AUTH_NONE String,
    FILING_DATE	 String,
    SUBMISSIONTYPE String,
    CIK String COMMENT "持仓机构 CIK 编号",
    PERIODOFREPORT String,
    FILINGMANAGER_NAME String COMMENT "持仓机构名字",
    FILINGMANAGER_CITY String COMMENT "持仓机构所在的地址",
    REPORT_DATE String COMMENT "对应的季度，格式为 2014-09-30，每年共 4 个季度上报，对应于 一季度 03-31、二季度 06-30、三季度 09-30、 和四季度 12-31"
) ENGINE = MergeTree()
ORDER BY (REPORT_DATE, CIK);
"""
def load_13F(path):
    print("processing:", path)
    if not os.path.exists(os.path.join(path, "RESULT.tsv")):
        submission = pd.read_csv(os.path.join(path, "SUBMISSION.tsv"), sep="\t")
        # print(submission)
        info_table = pd.read_csv(os.path.join(path, "INFOTABLE.tsv"), sep="\t")
        # print(info_table)
        cover_page = pd.read_csv(os.path.join(path, "COVERPAGE.tsv"), sep="\t")
        cover_page["REPORT_DATE"] = cover_page["REPORTCALENDARORQUARTER"]
        cover_page["REPORT_DATE"] = cover_page["REPORT_DATE"].apply(lambda x: datetime.strptime(x, "%d-%b-%Y"))
        cover_page_new = cover_page[["ACCESSION_NUMBER", "FILINGMANAGER_NAME", "FILINGMANAGER_CITY", "REPORT_DATE"]]
        # print(cover_page_new)
        df = (info_table.merge(submission, on="ACCESSION_NUMBER", how="left")
              .merge(cover_page_new, on="ACCESSION_NUMBER", how="left"))
        df.loc[df['REPORT_DATE'] <= "2022-09-30", 'VALUE'] = df.loc[df['REPORT_DATE'] <= "2022-09-30", 'VALUE'].apply(lambda x: x * 1000)
        df.to_csv(os.path.join(path, "RESULT.tsv"), sep=",", index=False)
        # print(df)


if __name__ == '__main__':
    dir_path = "/Users/kangtian/Documents/inv/F-13/"
    for path in os.listdir(dir_path):
        full_path = os.path.join(dir_path, path)
        if os.path.isdir(full_path):
            load_13F(full_path)

    # load_13F("/Users/kangtian/Documents/inv/F-13/2014q4_form13f.zip.unzip/")
