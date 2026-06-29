from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

#Recipe actions

class RecipeBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    ingredients: str
    instructions: str
    rating: int = Field(default = 1, ge=1, le=5)



class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: int
    image_path: Optional[str]= None

    model_config = ConfigDict(from_attributes=True)