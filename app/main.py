from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db, engine, Base
from . import schemas, crud, models
from .manager import manager
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Auction Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # "*" означає дозволити ВСІМ (Postman, Frontend, будь-хто)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/lots", response_model=list[schemas.LotResponse])
async def read_lots(db: AsyncSession = Depends(get_db)):
    return await crud.get_lots(db)

@app.post("/lots", response_model=schemas.LotResponse)
async def create_lot(lot: schemas.LotCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_lot(db, lot)

@app.post("/lots/{lot_id}/bids")
async def place_bid(lot_id: int, bid: schemas.BidCreate, db: AsyncSession = Depends(get_db)):
    lot = await crud.get_lot_for_update(db, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    if lot.status != "running":
        raise HTTPException(status_code=400, detail="Auction ended")
    if bid.amount <= lot.current:
        raise HTTPException(status_code=400, detail="Bid must be higher than current price")

    new_bid = await crud.create_bid(db, lot_id, bid)
    lot.current = bid.amount
    await db.commit()

    payload = {
        "type": "bid_placed",
        "lot_id": lot_id,
        "bidder": bid.bidder_name,
        "amount": bid.amount
    }
    await manager.broadcast(lot_id, payload)

    return {"message": "Bid accepted", "new_price": lot.current}

@app.websocket("/ws/lots/{lot_id}")
async def websocket_endpoint(websocket: WebSocket, lot_id: int):
    await manager.connect(websocket, lot_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, lot_id)
    except Exception as e:
        print(f"WebSocket Error: {e}")
        manager.disconnect(websocket, lot_id)