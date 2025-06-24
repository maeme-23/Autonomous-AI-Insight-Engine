from typing import List
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import logging
import os

class LLMAgent:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        self.llm = ChatOpenAI(model=model_name, temperature=0.1)
        self.last_prompt = None
        
        # Define the prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a precise research assistant. Strictly use ONLY the provided context to answer the user's question. 
            If the answer cannot be found in the context, say "I don't have enough information to answer that question."
            
            When answering:
            - Be concise and factual
            - Use bullet points when listing items
            - Always cite sources like [Source: document_name] for each fact
            
            Context:
            {context}"""),
            ("human", "{question}")
        ])
        
        # Create the chain
        self.chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )

    def generate_answer(self, question: str, docs: List[Document]) -> str:
        """Generate an answer based on the question and provided documents"""
        context = "\n\n".join([f"Document {doc.metadata.get('title', 'unknown')}:\n{doc.page_content}" for doc in docs])
        
        try:
            self.last_prompt = self.prompt_template.format(context=context, question=question)
            answer = self.chain.invoke({"context": context, "question": question})
            logging.info(f"Generated answer for question: {question}")
            return answer
        except Exception as e:
            logging.error(f"Failed to generate answer: {str(e)}")
            raise

    def stream_answer(self, question: str, docs: List[Document]):
        """Stream the answer token by token"""
        context = "\n\n".join([f"Document {doc.metadata.get('title', 'unknown')}:\n{doc.page_content}" for doc in docs])
        
        try:
            self.last_prompt = self.prompt_template.format(context=context, question=question)
            for chunk in self.chain.stream({"context": context, "question": question}):
                yield chunk
            logging.info(f"Streamed answer for question: {question}")
        except Exception as e:
            logging.error(f"Failed to stream answer: {str(e)}")
            yield "An error occurred while generating the answer."