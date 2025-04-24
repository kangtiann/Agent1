import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from haystack.utils import Secret
from haystack import component
from haystack.components.generators.chat import OpenAIChatGenerator
from typing import List, Optional, AnyStr

from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever

llm = OpenAIChatGenerator(
    model="deepseek-chat",
    api_base_url="https://api.deepseek.com/v1",
    api_key=Secret.from_env_var("DEEPSEEK_API_KEY"))


@component
class FearGreed:
    """
      A component collect FearGreed index
    """
    @component.output_types(df=pd.DataFrame)
    def run(self):
        """
      Query fear_greed index。

      :return: df Pandas DataFrame
      """
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        resp = requests.get(url=url, headers={
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "origin": "https://edition.cnn.com"
        })
        res = resp.json()
        df = pd.DataFrame.from_records(res["fear_and_greed_historical"]["data"], columns=['x', 'y', 'rating'])
        df = df.rename(columns={"x": "date", "y": "fear_and_greed"})
        df['date'] = pd.to_datetime(df['date'], unit="ms")
        df.set_index("date", inplace=True)
        return {"df": df}


@component
class GraphDrawer:
    @component.output_types(graph_path=AnyStr)
    def run(self, df: pd.DataFrame):
        """
        Draw graph for df.

        :param df: Pandas DataFrame.
        :return: The path of the graph.
        """
        df.plot(kind='line',
                title='fear-greed trending',
                xlabel='date',
                ylabel='fear-greed',
                grid=True,
                figsize=(15, 9),
                marker='o',
                linestyle='--')
        plt.show()
        return {"graph_path": "ok ..."}


query_pipeline = Pipeline()
query_pipeline.add_component("fear_greed", instance=FearGreed())
query_pipeline.add_component("graph_drawer", instance=GraphDrawer())
query_pipeline.connect("fear_greed", "graph_drawer")
res = query_pipeline.run({})
print(res["graph_drawer"])
