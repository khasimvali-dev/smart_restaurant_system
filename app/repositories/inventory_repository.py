from app.models.inventory import InventoryItem
from app.repositories.base_repository import BaseRepository


class InventoryRepository(BaseRepository):
    model = InventoryItem

    def low_stock(self):
        return [i for i in InventoryItem.query.all() if i.stock_status != "ok"]

    def get_by_name(self, name):
        return InventoryItem.query.filter_by(name=name).first()
