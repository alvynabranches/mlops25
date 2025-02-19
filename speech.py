import pyaudio
from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect

messages = []
app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept connection once, before the loop
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paFloat32, channels=1, rate=44100, output=True
    )
    try:
        while True:
            data = await websocket.receive_bytes()
            stream.write(data)
            
            await websocket.send_text("")
    except WebSocketDisconnect:
        print("WebSocket Disconnected Successfully!")
