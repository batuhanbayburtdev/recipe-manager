from typing import Optional
from sqlalchemy.orm import Session
from app.models import recipe as models
from app.schemas import recipe as schemas


def get_recipe(db: Session, recipe_id: int):
    """Fetches a recipe by its ID."""
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()


def get_recipes(db: Session, skip: int = 0, limit: int = 100):
    """Fetches a list of recipes."""
    return db.query(models.Recipe).offset(skip).limit(limit).all()


def create_recipe(db: Session, recipe: schemas.RecipeCreate, image_path: Optional[str] = None):
    """Creates a new recipe in the database."""
    db_recipe = models.Recipe(**recipe.model_dump(), image_path=image_path)

    db.add(db_recipe)        # Add a recipe to the session
    db.commit()              # Saves it to the database
    db.refresh(db_recipe)    # Reload to get auto-generated ID

    return db_recipe


def update_recipe(db: Session, recipe_id: int, recipe: schemas.RecipeCreate):
    """Updates a recipe's fields."""
    db_recipe = get_recipe(db, recipe_id)
    if not db_recipe:
        return None
    for key, value in recipe.model_dump().items():
        setattr(db_recipe, key, value)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


def delete_recipe(db: Session, recipe_id: int):
    """Deletes a recipe by ID from the database."""
    db_recipe = get_recipe(db, recipe_id)
    if db_recipe:
        db.delete(db_recipe)
        db.commit()

    return db_recipe


def update_recipe_image(db: Session, recipe_id: int, image_path: str):
    """Updates the image path for a recipe in the database."""
    db_recipe = get_recipe(db, recipe_id)
    if not db_recipe:           # guard against missing ID
        return None
    db_recipe.image_path = image_path
    db.commit()
    db.refresh(db_recipe)
    return db_recipe