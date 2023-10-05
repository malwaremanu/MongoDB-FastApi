from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

app = FastAPI()

mongo_url="mongodb+srv://malwaremanu:ManuMongodb1@cluster0.swwfxen.mongodb.net/sample_database?retryWrites=true&w=majority"

# Initialize the MongoDB client
client = AsyncIOMotorClient(mongo_url)

# Access the database and collection
db = client.get_database()
collection = db.get_collection("notes")

# Pydantic model for a note
class NoteCreate(BaseModel):
    title: str
    status: str

class Note(BaseModel):
    id: str
    title: str
    status: str


print(collection.insert_one({
  "title" : "sample note",
  "status" : "Active"
}))

@app.post("/notes/", response_model=Note)
async def create_note(note: NoteCreate):
    # Insert a new note into the database
    result = await collection.insert_one(note.dict())
    created_note = await collection.find_one({"_id": result.inserted_id})
    return {**{"id": created_note["_id"]}, **created_note}

@app.get("/notes/{note_id}", response_model=Note)
async def read_note(note_id: str):
    # Retrieve a note by ID from the database
    note = await collection.find_one({"_id": note_id})
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return {**{"id": note["_id"]}, **note}

@app.get("/notes/", response_model=list[Note])
async def list_notes():
    # Retrieve all notes from the database
    notes = []
    async for note in collection.find():
        notes.append({**{"id": note["_id"]}, **note})
    return notes

@app.put("/notes/{note_id}", response_model=Note)
async def update_note(note_id: str, note: NoteCreate):
    # Update a note by ID in the database
    await collection.update_one({"_id": note_id}, {"$set": note.dict()})
    updated_note = await collection.find_one({"_id": note_id})
    if updated_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return {**{"id": updated_note["_id"]}, **updated_note}

@app.delete("/notes/{note_id}", response_model=Note)
async def delete_note(note_id: str):
    # Delete a note by ID from the database
    deleted_note = await collection.find_one({"_id": note_id})
    if deleted_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    await collection.delete_one({"_id": note_id})
    return {**{"id": deleted_note["_id"]}, **deleted_note}