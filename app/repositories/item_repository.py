from app.extensions import db
from app.models.item import Item
from app.repositories.base_repository import BaseRepository


class ItemRepository(BaseRepository):
    model = Item

    def search(self, keyword=None, category_id=None, min_price=None, max_price=None,
               status=None, page=1, per_page=20):
        query = Item.query
        if keyword:
            like = f"%{keyword}%"
            query = query.filter(db.or_(Item.name.ilike(like), Item.sku.ilike(like)))
        if category_id:
            query = query.filter(Item.category_id == category_id)
        if min_price is not None:
            query = query.filter(Item.price >= min_price)
        if max_price is not None:
            query = query.filter(Item.price <= max_price)
        if status:
            query = query.filter(Item.status == status)
        query = query.order_by(Item.name.asc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_by_sku(self, sku):
        return Item.query.filter_by(sku=sku).first()

    def bulk_update_prices(self, item_ids, percent_change):
        """Apply a percentage change (+/-) to price for a batch of items."""
        items = Item.query.filter(Item.id.in_(item_ids)).all()
        for item in items:
            factor = 1 + (percent_change / 100)
            item.price = round(float(item.price) * factor, 2)
        db.session.commit()
        return items

    def low_stock_items(self, threshold=10):
        return Item.query.filter(Item.quantity_available <= threshold).all()
