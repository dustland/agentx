#!/usr/bin/env python3
"""
WordX Backend Service
AI-powered document processing backend using AgentX framework
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import uuid
from agentx import start_task
from dotenv import load_dotenv
from config import config

# Load environment variables
load_dotenv()

# Configure logging
log_level = logging.DEBUG if config.debug else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="WordX Backend",
    description="AI-powered document processing service",
    version="1.0.0",
    debug=config.debug
)

# CORS middleware for Office.js add-in
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for active tasks
active_tasks: Dict[str, Any] = {}

# Request/Response models
class DocumentProcessRequest(BaseModel):
    content: str
    task_description: str
    document_type: Optional[str] = "general"

class DocumentProcessResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    current_agent: Optional[str] = None
    progress: Optional[float] = None
    partial_results: Optional[List[Dict[str, Any]]] = []

class ChatRequest(BaseModel):
    task_id: str
    message: str

class ChatResponse(BaseModel):
    task_id: str
    response: str

# Helper functions
def get_config_path() -> Path:
    """Get the path to the team configuration file"""
    return config.get_agentx_config_path()

async def monitor_task_progress(task_id: str):
    """Monitor AgentX task progress and update status"""
    task = active_tasks[task_id]
    x = task["x"]
    
    try:
        # Define agent progression
        agent_sequence = ["document_reviewer", "content_editor", "formatter", "compliance_auditor"]
        
        while task["status"] == "processing":
            # Check if task is complete
            if hasattr(x, 'is_complete') and x.is_complete():
                task["status"] = "completed"
                task["progress"] = 1.0
                task["current_agent"] = None
                logger.info(f"Task {task_id} completed")
                break
            
            # Update progress based on current agent
            if hasattr(x, 'current_agent'):
                current_agent = x.current_agent
                if current_agent in agent_sequence:
                    agent_index = agent_sequence.index(current_agent)
                    task["progress"] = (agent_index + 0.5) / len(agent_sequence)
                    task["current_agent"] = current_agent
            
            # Get partial results if available
            if hasattr(x, 'get_partial_results'):
                partial = x.get_partial_results()
                if partial:
                    task["partial_results"].append(partial)
            
            await asyncio.sleep(2)  # Check every 2 seconds
            
    except Exception as e:
        logger.error(f"Error monitoring task {task_id}: {str(e)}")
        task["status"] = "error"
        task["progress"] = 0.0

async def create_document_processing_task(content: str, task_description: str, document_type: str) -> str:
    """Create a new document processing task"""
    task_id = str(uuid.uuid4())

    try:
        # Create the initial prompt for the agent team
        initial_prompt = f"""
        Document Processing Task:

        Document Type: {document_type}
        Task Description: {task_description}

        Document Content:
        {content}

        Please analyze this document and provide comprehensive improvements.
        """

        # Start the AgentX task
        config_path = get_config_path()
        x = await start_task(initial_prompt, str(config_path))

        # Store the task
        active_tasks[task_id] = {
            "x": x,
            "status": "processing",
            "current_agent": "document_reviewer",
            "progress": 0.0,
            "partial_results": []
        }

        # Start background monitoring
        asyncio.create_task(monitor_task_progress(task_id))

        logger.info(f"Created document processing task {task_id}")
        return task_id

    except Exception as e:
        logger.error(f"Failed to create task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "WordX Backend Service is running"}

@app.post("/api/process-document", response_model=DocumentProcessResponse)
async def process_document(request: DocumentProcessRequest, background_tasks: BackgroundTasks):
    """Start document processing with AgentX"""
    try:
        task_id = await create_document_processing_task(
            request.content,
            request.task_description,
            request.document_type
        )

        return DocumentProcessResponse(
            task_id=task_id,
            status="processing",
            message="Document processing started"
        )

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task-status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get the status of a processing task"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = active_tasks[task_id]

    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        current_agent=task["current_agent"],
        progress=task["progress"],
        partial_results=task["partial_results"]
    )

@app.get("/api/task-results/{task_id}")
async def get_task_results(task_id: str):
    """Get the final results of a completed task"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = active_tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task is not completed yet")

    try:
        x = task["x"]
        # Get the final output from AgentX
        final_result = await x.get_result() if hasattr(x, 'get_result') else str(x)
        
        return {
            "task_id": task_id,
            "status": "completed",
            "result": final_result,
            "partial_results": task["partial_results"]
        }
    except Exception as e:
        logger.error(f"Error getting results for task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_agents(request: ChatRequest):
    """Chat with the agent team for refinements"""
    if request.task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = active_tasks[request.task_id]
    x = task["x"]

    try:
        # Chat with the agent team
        response = await x.chat(request.message)

        return ChatResponse(
            task_id=request.task_id,
            response=response.text
        )

    except Exception as e:
        logger.error(f"Chat error for task {request.task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting WordX Backend Service...")
    print("📋 AgentX-powered document processing")
    print(f"🌐 Environment: {config.environment}")
    print(f"🌐 CORS enabled for: {', '.join(config.get_cors_origins())}")
    print(f"🔌 Backend running on {config.backend_host}:{config.backend_port}")
    print("-" * 50)

    uvicorn.run(
        app,
        host=config.backend_host,
        port=config.backend_port,
        log_level="debug" if config.debug else "info"
    )
