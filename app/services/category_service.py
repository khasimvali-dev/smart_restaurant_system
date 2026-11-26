from app.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self):
        self.repo = CategoryRepository()

    def create_category(self, name, description=None):
        if self.repo.get_by_name(name):
            raise ValueError(f"Category '{name}' already exists.")
        return self.repo.create(name=name, description=description)

    def update_category(self, category_id, **data):
        category = self.repo.get_by_id(category_id)
        if category is None:
            raise ValueError("Category not found.")
        return self.repo.update(category, **data)

    def delete_category(self, category_id):
        category = self.repo.get_by_id(category_id)
        if category is None:
            raise ValueError("Category not found.")
        if category.items.count() > 0:
            raise ValueError(
                "Cannot delete a category that still has menu items assigned to it."
            )
        self.repo.delete(category)

    def list_all(self):
        return self.repo.get_all()
