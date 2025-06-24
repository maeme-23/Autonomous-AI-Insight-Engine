from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import logging
from retriever import VectorRetriever
from llm_agent import LLMAgent
from cache import Cache
from database import DatabaseLogger
import uuid

app = FastAPI(
    title="Autonomous AI Insight Engine",
    description="API for querying a knowledge base with LLM-powered responses"
)

# Initialize components
retriever = VectorRetriever("data/", "sentence-transformers/all-MiniLM-L6-v2")
llm_agent = LLMAgent()
cache = Cache()
db_logger = DatabaseLogger("query_logs.db")

class QueryRequest(BaseModel):
    query: str
    stream: Optional[bool] = False

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    request_id: str

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query and return a structured response"""
    request_id = str(uuid.uuid4())
    
    # Check cache first
    cached_response = cache.get(request.query)
    if cached_response:
        logging.info(f"Returning cached response for query: {request.query}")
        return {**cached_response, "request_id": request_id}
    
    # Retrieve relevant documents
    try:
        docs = retriever.retrieve(request.query, top_k=3)
    except Exception as e:
        logging.error(f"Retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Retrieval failed")
    
    if not docs:
        raise HTTPException(status_code=404, detail="No relevant documents found")
    
    # Generate answer
    sources = [doc.metadata.get("title", f"doc_{i}") for i, doc in enumerate(docs)]
    
    if request.stream:
        def stream_generator():
            full_response = ""
            for chunk in llm_agent.stream_answer(request.query, docs):
                full_response += chunk
                yield chunk
            # Cache and log after streaming completes
            cache.set(request.query, {"answer": full_response, "sources": sources})
            db_logger.log_query(
                request_id=request_id,
                query=request.query,
                answer=full_response,
                sources=", ".join(sources),
                prompt=llm_agent.last_prompt
            )
        
        return StreamingResponse(stream_generator(), media_type="text/plain")
    
    else:
        try:
            answer = llm_agent.generate_answer(request.query, docs)
        except Exception as e:
            logging.error(f"LLM generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Answer generation failed")
        
        # Cache and log the response
        cache.set(request.query, {"answer": answer, "sources": sources})
        db_logger.log_query(
            request_id=request_id,
            query=request.query,
            answer=answer,
            sources=", ".join(sources),
            prompt=llm_agent.last_prompt
        )
        
        return {
            "answer": answer,
            "sources": sources,
            "request_id": request_id
        }

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    try:
        retriever.initialize()
        cache.initialize()
        db_logger.initialize()
        logging.info("All components initialized successfully")
    except Exception as e:
        logging.error(f"Startup initialization failed: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    retriever.cleanup()
    cache.cleanup()
    db_logger.cleanup()