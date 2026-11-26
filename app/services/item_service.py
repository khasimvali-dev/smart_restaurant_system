import csv
import io
from app.repositories.item_repository import ItemRepository


class ItemService:
    def __init__(self):
        self.repo = ItemRepository()

    def create_item(self, **data):
        if self.repo.get_by_sku(data.get("sku")):
            raise ValueError(f"SKU '{data['sku']}' already exists.")
        if float(data.get("price", 0)) < 0:
            raise ValueError("Price cannot be negative.")
        return self.repo.create(**data)

    def update_item(self, item_id, **data):
        item = self.repo.get_by_id(item_id)
        if item is None:
            raise ValueError("Item not found.")
        return self.repo.update(item, **data)

    def delete_item(self, item_id):
        item = self.repo.get_by_id(item_id)
        if item is None:
            raise ValueError("Item not found.")
        self.repo.delete(item)

    def search(self, **kwargs):
        return self.repo.search(**kwargs)

    def bulk_update_prices(self, item_ids, percent_change):
        return self.repo.bulk_update_prices(item_ids, percent_change)

    def low_stock_items(self, threshold=10):
        return self.repo.low_stock_items(threshold)

    def export_csv(self) -> str:
        items = self.repo.get_all()
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            ["SKU", "Name", "Category", "Price", "Discount %", "Tax %", "Qty", "Status"]
        )
        for item in items:
            writer.writerow(
                [
                    item.sku,
                    item.name,
                    item.category.name if item.category else "",
                    item.price,
                    item.discount_percent,
                    item.tax_percent,
                    item.quantity_available,
                    item.status,
                ]
            )
        return buffer.getvalue()
