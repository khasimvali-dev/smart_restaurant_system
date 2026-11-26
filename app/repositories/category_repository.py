from app.models.category import Category
from app.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository):
    model = Category

    def get_by_name(self, name):
        return Category.query.filter_by(name=name).first()
