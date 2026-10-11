import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash
from app.models.entities import (
    UserProfile, RoadmapStep, UserStepProgress, 
    Opportunity, PartnerLead, KnowledgeBaseItem, FeedbackItem
)
from app.models.schemas import (
    OnboardingFormRequest, FreeTextParseRequest, FreeTextParseResponse,
    RoadmapResponse, StepToggleRequest, ExperienceTranslateRequest,
    ExperienceTranslateResponse, ChatQueryRequest, ChatQueryResponse,
    LeadSubmitRequest, RegisterRequest, LoginRequest, AuthResponse,
    FeedbackCreateRequest, FeedbackResponse
)
from app.rules.engine import filter_and_rank_steps
from app.services.ai_service import ai_service

router = APIRouter()

# ================= 0. АВТОРИЗАЦІЯ ТА РЕЄСТРАЦІЯ (ТЕЛЕФОН + ПАРОЛЬ) =================
@router.post("/auth/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    clean_phone = req.phone.strip().replace(" ", "").replace("-", "")
    existing_user = db.query(UserProfile).filter(UserProfile.phone == clean_phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Користувач з таким номером телефону вже зареєстрований")

    # Якщо вже є анонімний токен, прив'язуємо цей профіль
    profile = None
    if req.existing_token:
        profile = db.query(UserProfile).filter(UserProfile.token == req.existing_token).first()

    if not profile:
        profile = UserProfile(token=str(uuid.uuid4()))
        db.add(profile)

    profile.phone = clean_phone
    profile.password_hash = get_password_hash(req.password)
    profile.full_name = req.full_name or "Ветеран"

    db.commit()
    db.refresh(profile)

    return AuthResponse(
        status="success",
        message="Реєстрація успішна! Тепер ви можете увійти на будь-якому смартфоні чи комп'ютері.",
        user_token=profile.token,
        phone=profile.phone,
        full_name=profile.full_name
    )

@router.post("/auth/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    clean_phone = req.phone.strip().replace(" ", "").replace("-", "")
    user = db.query(UserProfile).filter(UserProfile.phone == clean_phone).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Невірний номер телефону або пароль")

    return AuthResponse(
        status="success",
        message="Авторизація успішна!",
        user_token=user.token,
        phone=user.phone,
        full_name=user.full_name
    )

@router.get("/auth/me")
def get_current_user(token: str, db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.token == token).first()
    if not user:
        return {"authenticated": False}
    return {
        "authenticated": bool(user.phone),
        "phone": user.phone,
        "full_name": user.full_name,
        "user_token": user.token,
        "status": user.status,
        "city": user.city
    }

# ================= 1. ОНБОРДИНГ =================
@router.post("/onboarding/parse-text", response_model=FreeTextParseResponse)
def parse_free_text(req: FreeTextParseRequest):
    result = ai_service.parse_free_text_onboarding(req.text)
    return FreeTextParseResponse(
        parsed_profile=OnboardingFormRequest(**result["parsed_profile"]),
        summary_message=result["summary_message"],
        confidence=result.get("confidence", 0.95)
    )

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

# ================= 2. ДОРОЖНЯ КАРТА =================
@router.get("/roadmap", response_model=RoadmapResponse)
def get_roadmap(user_token: str, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.token == user_token).first()
    if not profile:
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

# ================= 3. ВІЙСЬКОВИЙ ПЕРЕКЛАДАЧ =================
@router.post("/experience/translate", response_model=ExperienceTranslateResponse)
def translate_experience(req: ExperienceTranslateRequest):
    result = ai_service.translate_military_experience(req.experience_text, req.target_area)
    return ExperienceTranslateResponse(**result)

# ================= 4. ВАКАНСІЇ ТА МОЖЛИВОСТІ =================
@router.get("/opportunities")
def get_opportunities(category: Optional[str] = None, type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Opportunity).filter(Opportunity.is_active == True)
    if category:
        query = query.filter(Opportunity.category == category)
    if type:
        query = query.filter(Opportunity.type == type)
    return query.order_by(Opportunity.created_at.desc()).all()

@router.post("/opportunities/interest")
def submit_lead(req: LeadSubmitRequest, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.token == req.user_token).first()
    if not profile:
        profile = UserProfile(token=req.user_token)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    lead = PartnerLead(
        user_id=profile.id,
        opportunity_id=req.opportunity_id,
        contact_channel=req.contact_channel,
        note=req.note
    )
    db.add(lead)
    db.commit()
    return {"status": "success", "message": "Дякуємо! Ваш контакт передано координатору програми."}

# ================= 5. ЧАТ RAG =================
@router.post("/chat/ask", response_model=ChatQueryResponse)
def chat_ask(req: ChatQueryRequest, db: Session = Depends(get_db)):
    items = db.query(KnowledgeBaseItem).all()
    knowledge_list = [{"topic": i.topic, "summary": i.summary, "official_source": i.official_source, "contacts": i.contacts or ""} for i in items]
    result = ai_service.answer_chat_query(req.question, knowledge_list)
    return ChatQueryResponse(**result)

# ================= 6. ЗАУВАЖЕННЯ ТА ВІДГУКИ (FEEDBACK) =================
@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(req: FeedbackCreateRequest, db: Session = Depends(get_db)):
    item = FeedbackItem(
        sender_name=req.sender_name,
        sender_contact=req.sender_contact,
        category=req.category or "general",
        message=req.message,
        source="web"
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return FeedbackResponse(
        id=item.id,
        sender_name=item.sender_name,
        sender_contact=item.sender_contact,
        category=item.category,
        message=item.message,
        source=item.source,
        status=item.status,
        created_at=item.created_at.strftime("%Y-%m-%d %H:%M")
    )

@router.get("/feedback/list", response_model=List[FeedbackResponse])
def get_feedback_list(db: Session = Depends(get_db)):
    items = db.query(FeedbackItem).order_by(FeedbackItem.created_at.desc()).limit(50).all()
    return [
        FeedbackResponse(
            id=i.id,
            sender_name=i.sender_name,
            sender_contact=i.sender_contact,
            category=i.category,
            message=i.message,
            source=i.source,
            status=i.status,
            created_at=i.created_at.strftime("%Y-%m-%d %H:%M")
        )
        for i in items
    ]

# ================= 7. КАБІНЕТ ПАРТНЕРА ТА ЧЕСНА СТАТИСТИКА =================
@router.get("/partner/analytics")
def get_partner_analytics(db: Session = Depends(get_db)):
    # Рахуємо ТІЛЬКИ реальних створених ветеранів, лідів та можливостей (без накруток)
    total_veterans = db.query(UserProfile).count()
    leads_count = db.query(PartnerLead).count()
    opportunities_count = db.query(Opportunity).filter(Opportunity.is_active == True).count()
    
    # Реальна аналітика потреб за базою даних
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

    feedback_count = db.query(FeedbackItem).count()

    return {
        "stats": {
            "total_veterans_registered": total_veterans,
            "total_leads_generated": leads_count,
            "active_opportunities": opportunities_count,
            "feedback_count": feedback_count
        },
        "community_needs": {
            "rehab_needed": needs_rehab,
            "goal_work": goal_work,
            "goal_business": goal_business,
            "goal_education": goal_education
        },
        "recent_leads": leads_data
    }
