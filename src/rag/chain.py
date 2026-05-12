import os
from typing import Dict, List

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from src.config import Config
from src.rag.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.vectorstore.store import get_retriever


def _build_llm(config: Config):
    from langchain_ollama import ChatOllama
    return ChatOllama(
        model=config.ollama_model,
        base_url=config.ollama_base_url,
        temperature=0.1,
    )


def format_docs(docs: List[Document]) -> str:
    formatted = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "n/a")
        doc_type = doc.metadata.get("doc_type", "n/a")
        formatted.append(
            f"[Quelle: {source}, Seite {page}, Typ: {doc_type}]\n{doc.page_content}"
        )
    return "\n\n".join(formatted)


def build_rag_chain(config: Config):
    retriever = get_retriever(config)
    llm = _build_llm(config)
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", USER_PROMPT_TEMPLATE)]
    )
    return (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )


def chain_with_sources(question: str, config: Config) -> Dict:
    retriever = get_retriever(config)
    docs = retriever.invoke(question)
    llm = _build_llm(config)
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", USER_PROMPT_TEMPLATE)]
    )
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": format_docs(docs), "question": question})
    return {"answer": answer, "documents": docs}