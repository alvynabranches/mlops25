from fastapi import FastAPI
from pydantic import BaseModel

class Data(BaseModel):
    price: float
    quantity: int

app = FastAPI()

@app.post("/calculate_total_price")
async def calculate_total_price(data: Data):
    return {"total_price": data.price * data.quantity}