import os
import time
import logging
import pandas as pd
from deepface import DeepFace
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

output_dir = os.path.join(os.path.dirname(__file__), "uploaded_images")
os.makedirs(output_dir, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class EmotionResult(BaseModel):
    emotion: str
    confidence: float


def detect_emotion(image_path: str) -> str:
    results = DeepFace.analyze(image_path, actions=["emotion"])
    new_results = [
        EmotionResult(
            emotion=result["dominant_emotion"], confidence=result["face_confidence"]
        )
        for result in results
    ][0]
    return new_results


def write_to_excel(file_path: str, emotion: str, confidence: float):
    """Function to write the results to an Excel file."""
    data = {
        "File Path": [file_path],
        "Emotion": [emotion],
        "Confidence": [confidence],
    }
    df = pd.DataFrame(data)

    # Append to Excel file with header
    excel_file = "emotion_results.xlsx"
    if os.path.exists(excel_file):
        df.to_excel(excel_file, mode="a", header=False, index=False)
    else:
        df.to_excel(excel_file, index=False)  # Write header when creating the file


@app.post("/detect-emotion/", response_model=EmotionResult)
async def upload_image(
    file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()
) -> dict:
    start_time = time.time()
    # Save the uploaded file
    image_path = os.path.join(output_dir, f"{file.filename}")
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    # Detect emotion
    try:
        emotion_result = detect_emotion(image_path)
        # Add the Excel writing task to the background
        background_tasks.add_task(
            write_to_excel,
            image_path,
            emotion_result.emotion,
            emotion_result.confidence,
        )
        elapsed_time = time.time() - start_time
        logging.info(f"Processed {file.filename} in {elapsed_time:.2f} seconds.")
        return emotion_result
    except Exception as e:
        logging.error(f"Error processing {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))