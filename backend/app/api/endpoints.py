import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import UserProfile, RoadmapStep, UserStepProgress, Opportunity, PartnerLead, KnowledgeBaseItem
from app.models.schemas import (
    OnboardingFormRequest, FreeTextParseRequest, FreeTextParseResponse,
    RoadmapResponse, StepToggleRequest, ExperienceTranslateRequest,
    ExperienceTranslateResponse, ChatQueryRequest, ChatQueryResponse,
    LeadSubmitRequest
)
from app.rules.engine import filter_and_rank_steps
from app.services.ai_service import ai_service

router = APIRouter()

# 1. Онбординг: вільний текст -> структурований профіль через AI
@router.post("/onboarding/parse-text", response_model=FreeTextParseResponse)
def parse_free_text(req: FreeTextParseRequest):
    result = ai_service.parse_free_text_onboarding(req.text)
    return FreeTextParseResponse(
        parsed_profile=OnboardingFormRequest(**result["parsed_profile"]),
        summary_message=result["summary_message"],
        confidence=result.get("confidence", 0.95)
    )

# 2. Збереження / оновлення профілю та створення анонімного токена
@router.post("/onboarding/save-profile")
def save_profile(req: OnboardingFormRequest, db: Session = Depends(get_db)):
    token = req.user_token or str(uuid.uuid4())
    
    profile = db.query(UserProfile).filter(UserProfile.token == token).first()
    if not profile:
        profile = UserProfile(
            token=token,
            status=req.status,
            region=req.region,
            city=req.city,
            demobilized_date=req.demobilized_date,
            health_status=req.health_status,
            primary_goal=req.primary_goal,
            education=req.education
        )
        db.add(profile)
    else:
        profile.status = req.status
        profile.region = req.region
        profile.city = req.city
        profile.demobilized_date = req.demobilized_date
        profile.health_status = req.health_status
        profile.primary_goal = req.primary_goal
        profile.education = req.education
    
    db.commit()
    db.refresh(profile)
    return {"user_token": profile.token, "status": "success", "message": "Профіль надійно збережено"}

# 3. Отримання персональної дорожньої карти (через Рушій правил)
@router.get("/roadmap", response_model=RoadmapResponse)
def get_roadmap(user_token: str, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.token == user_token).first()
    if not profile:
        # Створимо дефолтний профіль для зручності
        profile = UserProfile(token=user_token, status="ubd", health_status="none", primary_goal="work")
        db.add(profile)
        db.commit()
        db.refresh(profile)

    all_steps = db.query(RoadmapStep).all()
    completed_steps = db.query(UserStepProgress).filter(
        UserStepProgress.user_id == profile.id,
        UserStepProgress.is_completed == True
    ).all()
    completed_step_ids = {cs.step_id for cs in completed_steps}

    result = filter_and_rank_steps(profile, all_steps, completed_step_ids)
    
    return RoadmapResponse(
        user_token=user_token,
        total_steps=result["total_steps"],
        completed_steps=result["completed_steps"],
        progress_percentage=result["progress_percentage"],
        priority_steps=result["priority_steps"],
        stages=result["stages"]
    )

# 4. Перемикач статусу виконання кроку («Зроблено»)
@router.post("/roadmap/toggle-step")
def toggle_step(req: StepToggleRequest, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.token == req.user_token).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    progress = db.query(UserStepProgress).filter(
        UserStepProgress.user_id == profile.id,
        UserStepProgress.step_id == req.step_id
    ).first()

    if req.is_completed:
        if not progress:
            progress = UserStepProgress(user_id=profile.id, step_id=req.step_id, is_completed=True)
            db.add(progress)
        else:
            progress.is_completed = True
    else:
        if progress:
            db.delete(progress)

    db.commit()
    return {"status": "success", "step_id": req.step_id, "is_completed": req.is_completed}

# 5. Переклад військового досвіду на мову цивільного ринку праці
@router.post("/experience/translate", response_model=ExperienceTranslateResponse)
def translate_experience(req: ExperienceTranslateRequest):
    result = ai_service.translate_military_experience(req.experience_text, req.target_area)
    return ExperienceTranslateResponse(**result)

# 6. Каталог можливостей (вакансії, курси, гранти, реабілітація)
@router.get("/opportunities")
def get_opportunities(category: Optional[str] = None, type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Opportunity).filter(Opportunity.is_active == True)
    if category:
        query = query.filter(Opportunity.category == category)
    if type:
        query = query.filter(Opportunity.type == type)
    return query.all()

# 7. Дія "Зацікавило" — передача контакту партнеру
@router.post("/opportunities/interest")
def submit_lead(req: LeadSubmitRequest, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.token == req.user_token).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    lead = PartnerLead(
        user_id=profile.id,
        opportunity_id=req.opportunity_id,
        contact_channel=req.contact_channel,
        note=req.note
    )
    db.add(lead)
    db.commit()
    return {"status": "success", "message": "Дякуємо! Ваш контакт передано координатору програми."}

# 8. Чат із перевіреною базою знань (RAG-light)
@router.post("/chat/ask", response_model=ChatQueryResponse)
def chat_ask(req: ChatQueryRequest, db: Session = Depends(get_db)):
    items = db.query(KnowledgeBaseItem).all()
    knowledge_list = [{"topic": i.topic, "summary": i.summary, "official_source": i.official_source, "contacts": i.contacts or ""} for i in items]
    result = ai_service.answer_chat_query(req.question, knowledge_list)
    return ChatQueryResponse(**result)

# 9. Кабінет партнера та GovTech аналітика
@router.get("/partner/analytics")
def get_partner_analytics(db: Session = Depends(get_db)):
    total_veterans = db.query(UserProfile).count()
    leads_count = db.query(PartnerLead).count()
    opportunities_count = db.query(Opportunity).count()
    
    # Анонімна аналітика потреб громади
    needs_rehab = db.query(UserProfile).filter(UserProfile.health_status.in_(["rehab_needed", "prosthetics_needed"])).count()
    goal_work = db.query(UserProfile).filter(UserProfile.primary_goal == "work").count()
    goal_business = db.query(UserProfile).filter(UserProfile.primary_goal == "business").count()
    goal_education = db.query(UserProfile).filter(UserProfile.primary_goal == "education").count()

    leads = db.query(PartnerLead).order_by(PartnerLead.created_at.desc()).limit(15).all()
    leads_data = []
    for l in leads:
        leads_data.append({
            "id": l.id,
            "opportunity_title": l.opportunity.title if l.opportunity else "Загальний запит",
            "partner_name": l.opportunity.partner_name if l.opportunity else "Львівська ОВА",
            "contact_channel": l.contact_channel,
            "created_at": l.created_at.strftime("%Y-%m-%d %H:%M")
        })

    return {
        "stats": {
            "total_veterans_registered": total_veterans,
            "total_leads_generated": leads_count,
            "active_opportunities": opportunities_count
        },
        "community_needs": {
            "rehab_needed": needs_rehab,
            "goal_work": goal_work,
            "goal_business": goal_business,
            "goal_education": goal_education
        },
        "recent_leads": leads_data
    }
