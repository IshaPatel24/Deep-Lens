import os
import uuid
import json
import logging
import asyncio
from typing import Dict, List, Any
from fastapi import FastAPI, BackgroundTasks, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.db import init_db, save_session, get_session, get_all_sessions, get_evals
from backend.graph import run_research_pipeline
from backend.export.report_export import markdown_to_pdf, markdown_to_docx
from backend.eval.run_eval import run_benchmark

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DeepLens Backend", version="1.0.0")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stores for active sessions and queues
active_sessions_logs: Dict[str, List[Dict[str, Any]]] = {}
active_queues: Dict[str, asyncio.Queue] = {}

class ResearchRequest(BaseModel):
    query: str

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing SQLite database...")
    init_db()

@app.post("/api/research")
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Starts a research task in the background and returns a session ID."""
    session_id = str(uuid.uuid4())
    query = request.query
    
    # Initialize logs list and queue
    active_sessions_logs[session_id] = []
    active_queues[session_id] = asyncio.Queue()
    
    # Define log publisher callback
    async def publish_log(msg: Dict[str, Any]):
        active_sessions_logs[session_id].append(msg)
        if session_id in active_queues:
            await active_queues[session_id].put(msg)

    # Core background task runner
    async def run_pipeline_task():
        try:
            state = await run_research_pipeline(query, session_id, publish_log)
            # Save completed research to SQLite
            save_session(
                session_id=session_id,
                query=query,
                report=state.report,
                verified_data=state.verified_data,
                sources=state.sources,
                discarded_count=state.discarded_sources_count
            )
        except Exception as e:
            logger.error(f"Pipeline failed for session {session_id}: {e}")
            # Ensure failure is saved to history as well
            save_session(
                session_id=session_id,
                query=query,
                report=f"# Research Failed\n\nAn error occurred: {str(e)}",
                verified_data=[],
                sources=[],
                discarded_count=0
            )
        finally:
            # Clean up queue after task finishes and client consumes it
            await asyncio.sleep(10.0) # Grace period for client to fetch final messages
            if session_id in active_queues:
                del active_queues[session_id]

    background_tasks.add_task(run_pipeline_task)
    return {"session_id": session_id}

@app.get("/api/research/stream/{session_id}")
async def stream_research(session_id: str):
    """SSE endpoint streaming live agent activities to the frontend."""
    if session_id not in active_sessions_logs:
        # Check if it exists in DB (meaning it already finished previously)
        db_session = get_session(session_id)
        if db_session:
            # Yield completed final state immediately
            async def single_yield():
                yield f"data: {json.dumps({'agent': 'DeepLens System', 'status': 'completed', 'details': {'report': db_session['report'], 'verified_data': db_session['verified_data'], 'sources': db_session['sources'], 'discarded_count': db_session['discarded_count']}})}\n\n"
            return StreamingResponse(single_yield(), media_type="text/event-stream")
        raise HTTPException(status_code=404, detail="Session not found")

    async def sse_generator():
        # First send any existing cached logs (catch up)
        sent_count = 0
        for log in list(active_sessions_logs[session_id]):
            yield f"data: {json.dumps(log)}\n\n"
            sent_count += 1
            
        # Then stream remaining real-time logs
        if session_id in active_queues:
            queue = active_queues[session_id]
            # Skip messages we already sent in catch-up phase
            for _ in range(sent_count):
                if not queue.empty():
                    await queue.get()
                    queue.task_done()
                    
            while True:
                try:
                    # Non-blocking read with a timeout to detect disconnected clients
                    msg = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(msg)}\n\n"
                    queue.task_done()
                    
                    if msg.get("agent") == "DeepLens System" and msg.get("status") in ["completed", "failed"]:
                        break
                except asyncio.TimeoutError:
                    # Heartbeat to keep connection alive
                    yield "data: {\"heartbeat\": true}\n\n"
                except Exception as e:
                    logger.error(f"SSE stream error: {e}")
                    break

    return StreamingResponse(sse_generator(), media_type="text/event-stream")

@app.post("/api/research/stream")
async def research_stream_combined(request: ResearchRequest):
    """
    Combined SSE endpoint: receives query, runs pipeline, and streams all agent
    events back in a single long-lived HTTP response. Required for Vercel serverless
    where in-memory queues cannot be shared across separate request invocations.
    """
    session_id = str(uuid.uuid4())
    query = request.query

    async def generate():
        # Use an asyncio Queue as a channel between pipeline and generator
        queue: asyncio.Queue = asyncio.Queue()
        sentinel = object()

        async def publish_log(msg):
            await queue.put(msg)

        async def run_and_signal():
            try:
                state = await run_research_pipeline(query, session_id, publish_log)
                save_session(
                    session_id=session_id,
                    query=query,
                    report=state.report,
                    verified_data=state.verified_data,
                    sources=state.sources,
                    discarded_count=state.discarded_sources_count
                )
            except Exception as e:
                logger.error(f"Pipeline error for session {session_id}: {e}")
                await queue.put({
                    "session_id": session_id,
                    "agent": "DeepLens System",
                    "status": "failed",
                    "details": str(e),
                    "timestamp": __import__("time").time()
                })
            finally:
                await queue.put(sentinel)

        # Start pipeline as a concurrent task
        pipeline_task = asyncio.create_task(run_and_signal())

        try:
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=60.0)
                    if msg is sentinel:
                        break
                    yield f"data: {json.dumps(msg)}\n\n"
                    if msg.get("agent") == "DeepLens System" and msg.get("status") in ("completed", "failed"):
                        break
                except asyncio.TimeoutError:
                    yield 'data: {"heartbeat": true}\n\n'
        finally:
            pipeline_task.cancel()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # Disable nginx buffering
        }
    )

@app.get("/api/history")
async def list_history():
    """Returns all past research queries and summary stats."""
    return get_all_sessions()

@app.get("/api/sessions/{session_id}")
async def retrieve_session(session_id: str):
    """Fetches details of a research report."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.get("/api/export/{session_id}/{export_format}")
async def export_report(session_id: str, export_format: str):
    """Exports report as PDF, DOCX, or Markdown."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    report_text = session["report"]
    query_slug = session["query"].lower().replace(" ", "_")[:30]
    
    if export_format == "markdown":
        return Response(
            content=report_text,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=deeplens_{query_slug}.md"}
        )
    elif export_format == "pdf":
        pdf_bytes = markdown_to_pdf(report_text)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=deeplens_{query_slug}.pdf"}
        )
    elif export_format == "docx":
        docx_bytes = markdown_to_docx(report_text)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=deeplens_{query_slug}.docx"}
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid export format")

@app.get("/api/eval")
async def get_eval_results():
    """Fetches all past benchmark evaluation metrics."""
    return get_evals()

@app.post("/api/eval/run")
async def trigger_eval(background_tasks: BackgroundTasks):
    """Triggers an automated evaluation benchmark run in the background."""
    background_tasks.add_task(run_benchmark)
    return {"status": "Evaluation started in background."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
