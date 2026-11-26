from app.repositories.inventory_repository import InventoryRepository


class InventoryService:
    def __init__(self):
        self.repo = InventoryRepository()

    def add_inventory(self, **data):
        if self.repo.get_by_name(data.get("name")):
            raise ValueError("This ingredient is already tracked - update it instead.")
        return self.repo.create(**data)

    def update_inventory(self, inventory_id, **data):
        record = self.repo.get_by_id(inventory_id)
        if record is None:
            raise ValueError("Inventory record not found.")
        return self.repo.update(record, **data)

    def remove_inventory(self, inventory_id):
        record = self.repo.get_by_id(inventory_id)
        if record is None:
            raise ValueError("Inventory record not found.")
        self.repo.delete(record)

    def all_items(self):
        return self.repo.get_all()

    def low_stock_alerts(self):
        """Returns items split into out-of-stock vs low-stock for alert banners."""
        low = self.repo.low_stock()
        return {
            "out_of_stock": [i for i in low if i.stock_status == "out_of_stock"],
            "low_stock": [i for i in low if i.stock_status == "low_stock"],
        }
