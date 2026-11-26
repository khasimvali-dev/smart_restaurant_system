"""
Generic Repository Pattern implementation.

Every concrete repository (ItemRepository, BillRepository, ...) inherits
from this class and gets consistent CRUD behaviour. Services depend on
repositories, never directly on SQLAlchemy session/query internals - this
keeps persistence concerns out of business logic and makes the services
unit-testable with a fake repository.
"""
from app.extensions import db


class BaseRepository:
    model = None  # override in subclass

    def get_by_id(self, record_id):
        return self.model.query.get(record_id)

    def get_all(self):
        return self.model.query.all()

    def paginate(self, page=1, per_page=20, **filters):
        query = self.model.query
        for field, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, field) == value)
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def create(self, **kwargs):
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        db.session.commit()
        return instance

    def delete(self, instance):
        db.session.delete(instance)
        db.session.commit()

    def save(self, instance):
        db.session.add(instance)
        db.session.commit()
        return instance
