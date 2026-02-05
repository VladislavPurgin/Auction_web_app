from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas

# Змінюємо назву на get_lots, як того очікує main.py
async def get_lots(db: AsyncSession):
    # Згідно з ТЗ: "список активних лотів", тому фільтруємо за статусом 'running'
    result = await db.execute(select(models.Lot).where(models.Lot.status == "running"))
    return result.scalars().all()

async def create_lot(db: AsyncSession, lot: schemas.LotCreate):
    db_lot = models.Lot(
        title=lot.title,
        description=lot.description,
        start_price=lot.start_price,
        current=lot.start_price, # Початкова ціна дорівнює стартовій
        status="running" # Встановлюємо статус згідно з ТЗ
    )
    db.add(db_lot)
    await db.commit()
    await db.refresh(db_lot)
    return db_lot

async def get_lot_for_update(db: AsyncSession, lot_id: int):
    # Використовуємо with_for_update() для уникнення race condition при ставках
    result = await db.execute(
        select(models.Lot).where(models.Lot.id == lot_id).with_for_update()
    )
    return result.scalar_one_or_none()

async def create_bid(db: AsyncSession, lot_id: int, bid: schemas.BidCreate):
    db_bid = models.Bid(
        lot_id=lot_id,
        bidder_name=bid.bidder_name,
        amount=bid.amount
    )
    db.add(db_bid)
    await db.commit()
    await db.refresh(db_bid) # Додано refresh, щоб отримати id та створену дату
    return db_bid