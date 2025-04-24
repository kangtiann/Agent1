import logging
from haystack import tracing
from haystack.tracing.logging_tracer import LoggingTracer

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.DEBUG)

tracing.tracer.is_content_tracing_enabled = True  # to enable tracing/logging content (inputs/outputs)
tracing.enable_tracing(LoggingTracer(
    tags_color_strings={"haystack.component.input": "\x1b[1;31m", "haystack.component.name": "\x1b[1;34m"}))

from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument
from haystack.components.writers import DocumentWriter
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter

document_store = InMemoryDocumentStore()

# Indexing pipeline
indexing_pipeline = Pipeline()
indexing_pipeline.add_component(instance=LinkContentFetcher(), name="fetcher")
indexing_pipeline.add_component(instance=HTMLToDocument(), name="converter")
indexing_pipeline.add_component(instance=DocumentCleaner(), name="cleaner")
indexing_pipeline.add_component(instance=DocumentSplitter(split_by="sentence", split_length=5, split_overlap=1),
                                name="splitter")
indexing_pipeline.add_component(instance=DocumentWriter(document_store=document_store), name="writer")

indexing_pipeline.connect("fetcher.streams", "converter.sources")
indexing_pipeline.connect("converter.documents", "cleaner")
indexing_pipeline.connect("cleaner", "splitter")
indexing_pipeline.connect("splitter", "writer.documents")

# index some documentation pages to use for RAG
indexing_pipeline.run({
    "fetcher": {
        "urls": [
            "https://docs.haystack.deepset.ai/docs/generators-vs-chat-generators",
            "https://docs.haystack.deepset.ai/docs/ollamagenerator",
            "https://haystack.deepset.ai/overview/quick-start",
            "https://haystack.deepset.ai/overview/intro"
        ]}})

from haystack.components.routers import ConditionalRouter

main_routes = [
    {
        "condition": "{{'N0_ANSWER' in replies[0].text.replace('\n', '')}}",
        "output": "{{query}}",
        "output_name": "go_web",
        "output_type": str,
    },
    {
        "condition": "{{'NO_ANSWER' not in replies[0].text.replace('\n', '')}}",
        "output": "{{replies[0].text}}",
        "output_name": "answer",
        "output_type": str,
    },
]

agent_prompt_template = """<start_of_turn>user
{% if web_documents %}
    You were asked to answer the following query given the documents retrieved from Haystack's documentation but the context was not enough.
    Here is the user question: {{ query }}
    Context:
    {% for document in documents %}
        {{document.content}}
    {% endfor %}
    {% for document in web_documents %}
    URL: {{document.meta.link}}
    TEXT: {{document.content}}
    ---
    {% endfor %}
    Answer the question based on the given context.
    If you have enough context to answer this question, return your answer with the used links.
    If you don't have enough context to answer, say 'N0_ANSWER'.
{% else %}
Answer the following query based on the documents retrieved from Haystack's documentation.

Documents:
{% for document in documents %}
  {{document.content}}
{% endfor %}

Query: {{query}}

If you have enough context to answer this question, just return your answer
If you don't have enough context to answer, say 'N0_ANSWER'.
{% endif %}

<end_of_turn>
<start_of_turn>model
"""

from haystack import Pipeline
from haystack.utils import Secret
from haystack.dataclasses import ChatMessage
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.websearch import SerperDevWebSearch
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator

from haystack_integrations.components.generators.ollama import OllamaGenerator


self_reflecting_agent = Pipeline(max_runs_per_component=5)
self_reflecting_agent.add_component("retriever", InMemoryBM25Retriever(document_store=document_store, top_k=3))
template = [ChatMessage.from_user(agent_prompt_template)]
self_reflecting_agent.add_component("prompt_builder_for_agent", ChatPromptBuilder(template=template))
self_reflecting_agent.add_component("llm_for_agent", OpenAIChatGenerator(
    model="deepseek-chat",
    api_base_url="https://api.deepseek.com/v1",
    api_key=Secret.from_env_var("DEEPSEEK_API_KEY")))
self_reflecting_agent.add_component("web_search", SerperDevWebSearch())
self_reflecting_agent.add_component("router", ConditionalRouter(main_routes))

self_reflecting_agent.connect("retriever.documents", "prompt_builder_for_agent.documents")
self_reflecting_agent.connect("prompt_builder_for_agent", "llm_for_agent")
self_reflecting_agent.connect("llm_for_agent.replies", "router.replies")
self_reflecting_agent.connect("router.go_web", "web_search.query")
self_reflecting_agent.connect("web_search.documents", "prompt_builder_for_agent.web_documents")

self_reflecting_agent.draw("/tmp/1.png")


query = "未来10天北京天气怎么样?"
result = self_reflecting_agent.run(
    {"retriever": {"query": query}, "prompt_builder_for_agent": {"query": query}, "router": {"query": query}},
    include_outputs_from={"retriever", "router", "llm_for_agent", "web_search", "prompt_builder_for_agent"})
print(result["router"]["answer"])
