import io
import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from PIL import Image, UnidentifiedImageError

from app.core.database import get_db
from app.schemas import recipe as schemas
from app.services import crud

router = APIRouter()

# --- Configuration & Security Constants ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
EXT_MAP = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# --- Standard CRUD Endpoints ---

@router.post("/recipes/", response_model=schemas.Recipe, status_code=status.HTTP_201_CREATED)
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    return crud.create_recipe(db=db, recipe=recipe)


@router.get("/recipes/", response_model=List[schemas.Recipe])
def read_recipes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_recipes(db, skip=skip, limit=limit)


@router.get("/recipes/{recipe_id}", response_model=schemas.Recipe)
def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = crud.get_recipe(db, recipe_id=recipe_id)
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return db_recipe


@router.put("/recipes/{recipe_id}", response_model=schemas.Recipe)
def update_recipe(recipe_id: int, recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    updated = crud.update_recipe(db, recipe_id, recipe)
    if updated is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return updated


@router.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = crud.get_recipe(db, recipe_id=recipe_id)
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    crud.delete_recipe(db, recipe_id=recipe_id)
    return None


# --- Secure File Upload Endpoint ---

@router.post("/recipes/{recipe_id}/image", response_model=schemas.Recipe)
def upload_recipe_image(
        recipe_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    # 1. Verify the recipe exists before accepting the file
    db_recipe = crud.get_recipe(db, recipe_id=recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # 2. Security Check #1: Declared content type (cheap first filter, client-supplied)
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, and WebP are allowed."
        )

    # 3. Security Check #2: File size
    file_bytes = file.file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB."
        )

    # 4. Security Check #3: Verify the bytes are ACTUALLY an image (cannot be spoofed)
    #    content_type can be faked; this inspects the real file contents.
    try:
        Image.open(io.BytesIO(file_bytes)).verify()
    except (UnidentifiedImageError, Exception):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a valid image."
        )

    # 5. Generate secure, unique filename (extension from validated type, not client input)
    file_extension = EXT_MAP[file.content_type] #type: ignore
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 6. Save the file (write the bytes we already validated)
    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)

    # 7. Update database — store forward-slash path so it works in URLs
    url_path = file_path.replace("\\", "/")
    updated_recipe = crud.update_recipe_image(db, recipe_id, url_path)

    return updated_recipe