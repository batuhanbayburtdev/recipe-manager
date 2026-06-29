from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base

class Recipe(Base):
    __tablename__ = "recipe"


    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    ingredients = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    rating = Column(Integer, default=1)
    image_path = Column(String, nullable=True)