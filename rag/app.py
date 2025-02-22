import os
import secrets
import aiofiles
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils import load_pdf, get_answers, delete_collection

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DOCS_DIR = os.path.join(os.path.dirname(__file__))


class Data(BaseModel):
    query: str
    k: int = 5


@app.get("/")
async def home():
    return JSONResponse({"status": "working"})


@app.post("/rag", status_code=201)
async def rags(files: list[UploadFile]):
    """
    Endpoint to receive and process uploaded PDF files.

    Parameters:
    - files: list[UploadFile] - List of uploaded files.

    Returns:
    - JSONResponse: Response containing the unique document ID or an error message.
    """
    unique_hash = secrets.token_hex(16)
    if pdf_files := [file for file in files if file.filename.endswith(".pdf")]:
        os.mkdir(path := os.path.join(DOCS_DIR, unique_hash))
        for n, file in enumerate(pdf_files):
            content = await file.read()
            async with aiofiles.open(f"{path}/{n}.pdf", "wb") as handle:
                await handle.write(content)
                await handle.close()
        load_pdf(path, unique_hash)
        os.system(f"rm -rf {path}")
        return JSONResponse({"documentID": unique_hash}, 201)
    return JSONResponse({"status": "At least one PDF file is required"}, 422)


@app.post("/qa/{documentID}", status_code=201)
async def get_answer(documentID: str, data: Data):
    # if not os.path.isdir(os.path.join(DOCS_DIR, documentID)):
    #     return JSONResponse({"status": "Document ID not found"})
    answers = get_answers(data.query, documentID, data.k)
    return JSONResponse(answers, status_code=201)


@app.delete("/rag/{documentID}", status_code=200)
async def delete_rag(documentID: str):
    """
    Endpoint to delete a document based on its unique document ID.

    Parameters:
    - documentID: str - The unique identifier for the document to be deleted.

    Returns:
    - JSONResponse: A response indicating whether the deletion was successful or not.
    """
    # Attempt to delete the document collection with the given document ID.
    # If the deletion is successful, return a success message.
    if delete_collection(documentID):
        return JSONResponse({"status": "Deleted Successfully!"})
    # If the document ID does not exist or the deletion was unsuccessful,
    # return an error message indicating the document ID could not be found.
    return JSONResponse({"status": "Could not find Document ID"}, 422)
