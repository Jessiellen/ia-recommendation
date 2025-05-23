# app/api/endpoints/recommendations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload # Importar joinedload
from typing import List
from app.schemas import User, Recommendation
from app.database import get_db
from app.core.security import get_current_user
from app.agents.recommendation_agent import RecommendationAgent
from app.models import User as UserModel 

router = APIRouter()

@router.get("/recommendations/", response_model=List[Recommendation])
async def get_recommendations(
    current_user_schema: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    try:
        user_from_db = db.query(UserModel).options(joinedload(UserModel.products)).filter(UserModel.id == current_user_schema.id).first()
        if not user_from_db:
            raise HTTPException(status_code=404, detail="User not found in database.")

        user_products_info = ", ".join([p.name for p in user_from_db.products]) if user_from_db.products else "nenhum histórico de produtos relevante"

        agent = RecommendationAgent()

        recommendations = await agent.generate_recommendations(user_from_db, user_products_info)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")