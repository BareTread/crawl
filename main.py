from fastapi import FastAPI, HTTPException
from crawl4ai import AsyncWebCrawler
from pydantic import BaseModel
from typing import Optional, Union, List
import asyncio
import uuid

app = FastAPI()
tasks = {}

class CrawlRequest(BaseModel):
    urls: Union[str, List[str]]
    priority: Optional[int] = 10

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/crawl")
async def crawl(request: CrawlRequest):
    task_id = str(uuid.uuid4())
    
    async def process_task():
        try:
            async with AsyncWebCrawler(verbose=True) as crawler:
                result = await crawler.arun(
                    url=request.urls[0] if isinstance(request.urls, list) else request.urls,
                    priority=request.priority
                )
                tasks[task_id] = {
                    "status": "completed",
                    "result": {
                        "markdown": result.markdown,
                        "success": result.success
                    }
                }
        except Exception as e:
            tasks[task_id] = {
                "status": "failed",
                "error": str(e)
            }
    
    tasks[task_id] = {"status": "processing"}
    asyncio.create_task(process_task())
    return {"task_id": task_id}

@app.get("/task/{task_id}")
async def get_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]