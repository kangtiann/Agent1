import torch
from transformers import AutoModel
from numpy.linalg import norm

# cos_sim = lambda a, b: (a @ b.T) / (norm(a)*norm(b))
# model = AutoModel.from_pretrained('jinaai/jina-embeddings-v2-base-zh', trust_remote_code=True, torch_dtype=torch.bfloat16)
# embeddings = model.encode(['How is the weather today?', '今天天气怎么样?'])
# print(embeddings[0], embeddings[1])
# print(cos_sim(embeddings[0], embeddings[1]))
#
# embedding = model.encode('How is the weather today?')
# print(embedding)


# from sentence_transformers import SentenceTransformer
#
# # 下载并保存 Jina Embeddings 模型到本地目录
# model = SentenceTransformer("jinaai/jina-embeddings-v2-base-zh")
# model.save("/Users/kangtian/Documents/master/Agent1/models/jina-embeddings-v2-base-zh")

from langchain.embeddings import HuggingFaceEmbeddings

# 配置本地模型路径
model_name = "/Users/kangtian/Documents/master/Agent1/models/jina-embeddings-v2-base-zh"
model_kwargs = {'device': 'cpu'}  # 或 'cuda' 使用 GPU

# 创建 Jina Embeddings 实例
jina_embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs={'normalize_embeddings': True},
)

texts = ["Hello, world!", "LangChain is awesome."]
embeddings = jina_embeddings.embed_documents(texts)
print(f"向量维度: {len(embeddings[0])}")  # 预期输出: 768 (jina-base-v2 的维度)