from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Product
from ..schemas import Recommendation
from ..agents.recommendation_agent import RecommendationAgent
from typing import List

router = APIRouter()

@router.get("/recommendations/{user_id}", response_model=List[Recommendation])
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    agent = RecommendationAgent()
    recommendations = agent.generate_recommendations(user)

    return recommendations