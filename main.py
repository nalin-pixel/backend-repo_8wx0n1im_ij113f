import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Call, CallEvent

app = FastAPI(title="NEOSERVICE API", description="Simple voice calling backend scaffolding for NEOSERVICE")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "NEOSERVICE backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# --------- Voice call endpoints (scaffold) ----------
class StartCallRequest(BaseModel):
    title: Optional[str] = None
    participant: Optional[str] = None


@app.post("/api/calls")
def start_call(payload: StartCallRequest):
    try:
        call = Call(title=payload.title, participant=payload.participant)
        call_id = create_document("call", call)
        return {"call_id": call_id, "status": "active"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calls")
def list_calls(limit: int = 20):
    try:
        docs = get_documents("call", {}, limit)
        # Convert ObjectId and datetime to string for JSON
        def serialize(doc: Dict[str, Any]):
            doc["_id"] = str(doc.get("_id"))
            for k, v in list(doc.items()):
                if hasattr(v, "isoformat"):
                    doc[k] = v.isoformat()
            return doc
        return [serialize(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AddEventRequest(BaseModel):
    call_id: str
    type: str
    text: Optional[str] = None


@app.post("/api/calls/event")
def add_event(payload: AddEventRequest):
    """Append an event (e.g., transcript or status) to a call"""
    try:
        if db is None:
            raise Exception("Database not available")
        oid = ObjectId(payload.call_id)
        event = CallEvent(call_id=payload.call_id, type=payload.type, text=payload.text).model_dump()
        db["call"].update_one({"_id": oid}, {"$push": {"events": event}, "$set": {"updated_at": db["call"].find_one({"_id": oid}).get("updated_at")}})
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class EndCallRequest(BaseModel):
    call_id: str


@app.post("/api/calls/end")
def end_call(payload: EndCallRequest):
    try:
        if db is None:
            raise Exception("Database not available")
        oid = ObjectId(payload.call_id)
        # calculate duration if started_at exists
        call_doc = db["call"].find_one({"_id": oid})
        if not call_doc:
            raise HTTPException(status_code=404, detail="Call not found")
        from datetime import datetime, timezone
        started_at = call_doc.get("started_at")
        duration = None
        ended_at = datetime.now(timezone.utc)
        if started_at:
            try:
                duration = int((ended_at - started_at).total_seconds())
            except Exception:
                duration = None
        db["call"].update_one(
            {"_id": oid},
            {"$set": {"status": "ended", "ended_at": ended_at, "duration_seconds": duration}}
        )
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------- Schema endpoint for viewer ---------------
@app.get("/schema")
def get_schema_info():
    return {
        "models": ["User", "Product", "Call", "CallEvent"]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
