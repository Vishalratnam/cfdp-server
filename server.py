import os
import random
import hashlib
import base64
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request

CHUNK_SIZE = 1024
TOTAL_CHUNKS = 100
DATA_FILE = b"A" * CHUNK_SIZE * TOTAL_CHUNKS
CHUNK_HASHES = []
CORRUPT_PROB = 0.6
DROP_PROB = 0.4
DELAY_PROB = 0.5

CHUNKS = []
for i in range(TOTAL_CHUNKS):
    chunk_data = DATA_FILE[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]
    sha = hashlib.sha256(chunk_data).hexdigest()
    CHUNK_HASHES.append(sha)
    encoded_data = base64.b64encode(chunk_data).decode()
    CHUNKS.append({
        "sequence": i,
        "data": encoded_data,
        "sha256": sha
    })

FULL_FILE_HASH = hashlib.sha256(DATA_FILE).hexdigest()

app = FastAPI()

@app.get("/manifest")
async def get_manifest():
    return {
        "total_chunks": TOTAL_CHUNKS,
        "checksum": FULL_FILE_HASH,
        "chunk_hashes": CHUNK_HASHES
    }

@app.get("/chunk/{chunk_id}")
async def get_chunk(chunk_id: int, request: Request):
    if chunk_id < 0 or chunk_id >= TOTAL_CHUNKS:
        raise HTTPException(status_code=404, detail="Chunk not found")

    if random.random() < DROP_PROB:
        raise HTTPException(status_code=500, detail="Simulated server error")

    if random.random() < DELAY_PROB:
        import asyncio
        await asyncio.sleep(random.uniform(0.6, 1))

    chunk = CHUNKS[chunk_id]

    if random.random() < CORRUPT_PROB:
        corrupted_data = os.urandom(CHUNK_SIZE)
        corrupted_encoded = base64.b64encode(corrupted_data).decode()
        corrupted_sha = hashlib.sha256(corrupted_data).hexdigest()

        return JSONResponse(content={
            "sequence": chunk["sequence"],
            "data": corrupted_encoded,
            "sha256": corrupted_sha
        })

    return JSONResponse(content=chunk)
