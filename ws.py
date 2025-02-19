from fastapi import FastAPI
from ollama import AsyncClient, ChatResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect

messages = []
app = FastAPI()
client = AsyncClient()


async def chat(messages: list) -> ChatResponse:
    new_messages = messages.copy()
    res = await client.chat(model="qwen2.5:0.5b", messages=messages)
    new_messages.append({"role": "assistant", "content": res.message.content})
    return new_messages


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept connection once, before the loop
    messages = []  # Initialize messages list outside the loop
    try:
        while True:
            data = await websocket.receive_text()
            messages.append({"role": "user", "content": data})
            messages = await chat(messages)
            await websocket.send_text(messages[-1]["content"])
    except WebSocketDisconnect:
        print("WebSocket Disconnected Successfully!")

