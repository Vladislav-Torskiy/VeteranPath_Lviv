from typing import List, Optional
from pydantic import BaseModel, Field

class OnboardingFormRequest(BaseModel):
    status: str = Field(..., description="Статус: ubd, active_duty, disability, family_member")
    region: str = Field("Львівська область", description="Область")
    city: str = Field("Львів", description="Місто/Громада")
    demobilized_date: Optional[str] = None
    health_status: str = Field("none", description="none, rehab_needed, prosthetics_needed, psychological")
    primary_goal: str = Field("work", description="work, business, education, health")
    education: Optional[str] = "Вища / середня спеціальна"
    user_token: Optional[str] = None

class FreeTextParseRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Розповідь ветерана про себе своїми словами")

class FreeTextParseResponse(BaseModel):
    parsed_profile: OnboardingFormRequest
    summary_message: str
    confidence: float

class RoadmapStepResponse(BaseModel):
    id: str
    title: str
    stage: str
    stage_title: str
    priority: int
    category: str
    short_description: str
    required_documents: List[str]
    where_to_go: str
    estimated_time: str
    official_source: str
    last_verified_at: str
    is_completed: bool = False

class RoadmapResponse(BaseModel):
    user_token: str
    total_steps: int
    completed_steps: int
    progress_percentage: int
    priority_steps: List[RoadmapStepResponse]
    stages: dict

class StepToggleRequest(BaseModel):
    user_token: str
    step_id: str
    is_completed: bool

class ExperienceTranslateRequest(BaseModel):
    experience_text: str = Field(..., min_length=5, description="Опис служби, обов'язків, посади")
    target_area: Optional[str] = "logistics_management"

class ExperienceTranslateResponse(BaseModel):
    civilian_skills: List[str]
    resume_bullet_points: List[str]
    recommended_roles: List[str]
    skill_gaps_and_courses: List[dict]

class ChatQueryRequest(BaseModel):
    question: str
    user_token: Optional[str] = None

class ChatQueryResponse(BaseModel):
    answer: str
    sources: List[str]
    recommended_hotlines: List[str]

class LeadSubmitRequest(BaseModel):
    user_token: str
    opportunity_id: str
    contact_channel: str
    note: Optional[str] = None

# ================= AUTH SCHEMAS =================
class RegisterRequest(BaseModel):
    phone: str = Field(..., description="Номер телефону ветерана (+380...)")
    password: str = Field(..., min_length=4, description="Пароль для доступу з комп'ютера і смартфона")
    full_name: Optional[str] = None
    existing_token: Optional[str] = None # Якщо вже проходив анонімний онбординг, прив'язати його

class LoginRequest(BaseModel):
    phone: str = Field(..., description="Номер телефону ветерана")
    password: str = Field(..., description="Пароль")

class AuthResponse(BaseModel):
    status: str
    message: str
    user_token: str
    phone: str
    full_name: Optional[str] = None

# ================= FEEDBACK SCHEMAS =================
class FeedbackCreateRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Текст зауваження або пропозиції")
    sender_name: Optional[str] = None
    sender_contact: Optional[str] = None
    category: Optional[str] = "general"

class FeedbackResponse(BaseModel):
    id: int
    sender_name: Optional[str]
    sender_contact: Optional[str]
    category: str
    message: str
    source: str
    status: str
    created_at: str
