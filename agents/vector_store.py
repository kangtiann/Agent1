from langchain_community.vectorstores import Clickhouse, ClickhouseSettings
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.utils.math import cosine_similarity


class ClickHouseVectorStore:
    def __init__(self):
        # self.model = AutoModel.from_pretrained('jinaai/jina-embeddings-v2-base-zh',
        #                                        trust_remote_code=True, torch_dtype=torch.bfloat16)

        settings = ClickhouseSettings(username="agent", database="inv", table="vector",
                                      index_type="vector_similarity",
                                      index_param=["hnsw", "L2Distance"]
                                      )

        # 配置本地模型路径
        model_name = "/Users/kangtian/Documents/master/Agent1/models/jina-embeddings-v2-base-zh"
        model_kwargs = {'device': 'cpu'}  # 或 'cuda' 使用 GPU

        # 创建 Jina Embeddings 实例
        jina_embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vector_store = Clickhouse(jina_embeddings, config=settings)

    def save_texts(self, texts):
        self.vector_store.add_texts(texts)

    def save_doc(self, doc, metadata=None, similarity_threshold=0.8):
        if metadata is None:
            metadata = dict()

        unique_doc = None
        # 检查是否存在相似文档
        similar_docs = self.vector_store.similarity_search(doc, k=1)
        if not similar_docs:
            unique_doc = doc
        else:
            # 计算与最相似文档的匹配度
            embedding = self.vector_store.embeddings.embed_query(doc)
            existing_embedding = self.vector_store.embeddings.embed_query(similar_docs[0].page_content)
            similarity = cosine_similarity([embedding], [existing_embedding])[0][0]
            if similarity < similarity_threshold:
                unique_doc = doc

        if unique_doc:
            self.vector_store.add_documents([Document(
                page_content=unique_doc,
                metadata=metadata,
            )])
        else:
            print("doc already exists, skip ~")

        if unique_doc:
            return True
        else:
            return False

    def query(self, text, search_type="similarity"):
        return self.vector_store.search(text, search_type=search_type)


vector_store = ClickHouseVectorStore()


if __name__ == '__main__':
    store = ClickHouseVectorStore()
    # store.save_doc("今天是晴天")
    print(store.query("今天是？"))

