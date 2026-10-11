import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = Column(String(64), unique=True, index=True, nullable=False)
    
    # Анонімні параметри профілю
    status = Column(String(64), nullable=True) # "ubd", "active_duty", "disability", "family_member"
    region = Column(String(64), default="Львівська область")
    city = Column(String(64), default="Львів")
    demobilized_date = Column(String(64), nullable=True)
    health_status = Column(String(64), default="none") # "none", "rehab_needed", "prosthetics_needed", "psychological"
    primary_goal = Column(String(64), default="work") # "work", "business", "education", "health"
    education = Column(String(64), nullable=True)
    free_text_bio = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Зв'язки
    completed_steps = relationship("UserStepProgress", back_populates="user", cascade="all, delete-orphan")
    leads = relationship("PartnerLead", back_populates="user", cascade="all, delete-orphan")


class RoadmapStep(Base):
    __tablename__ = "roadmap_steps"

    id = Column(String(64), primary_key=True) # slug e.g. "step-ubd-status"
    title = Column(String(255), nullable=False)
    stage = Column(String(64), nullable=False) # "week_1", "month_1", "month_3", "long_term"
    priority = Column(Integer, default=1) # 1 - критично, 2 - середньо, 3 - факультативно
    category = Column(String(64), nullable=False) # "documents", "finances", "health", "career", "business"
    short_description = Column(Text, nullable=False)
    required_documents = Column(JSON, default=list) # ["паспорт", "витяг з наказу..."]
    where_to_go = Column(String(255), nullable=False) # "ЦНАП м. Львів / Unbroken / Дія"
    estimated_time = Column(String(64), nullable=False) # "5-10 робочих днів"
    official_source = Column(String(512), nullable=False)
    last_verified_at = Column(String(32), default="2025-01-15")
    
    # Умови показу для Rule Engine
    condition_status = Column(JSON, default=list) # ["ubd", "active_duty"] or empty for all
    condition_health = Column(JSON, default=list) # ["rehab_needed", "prosthetics_needed"]
    condition_goal = Column(JSON, default=list) # ["work", "business"]


class UserStepProgress(Base):
    __tablename__ = "user_step_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("user_profiles.id"), nullable=False)
    step_id = Column(String(64), ForeignKey("roadmap_steps.id"), nullable=False)
    is_completed = Column(Boolean, default=True)
    completed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile", back_populates="completed_steps")


class Opportunity(Base):
    """Вакансії, програми перекваліфікації, гранти та реабілітація"""
    __tablename__ = "opportunities"

    id = Column(String(64), primary_key=True)
    partner_id = Column(String(64), nullable=False)
    partner_name = Column(String(128), nullable=False)
    title = Column(String(255), nullable=False)
    type = Column(String(32), nullable=False) # "vacancy", "course", "grant", "rehab"
    category = Column(String(64), nullable=False) # "IT", "logistics", "production", "medical", "business"
    location = Column(String(128), default="Львів")
    description = Column(Text, nullable=False)
    benefits = Column(Text, nullable=True) # "Ветеранський ментор, гнучкий графік..."
    contact_url = Column(String(512), nullable=True)
    salary_range = Column(String(64), nullable=True)
    is_active = Column(Boolean, default=True)

    leads = relationship("PartnerLead", back_populates="opportunity")


class PartnerLead(Base):
    """Анонімний або добровільно переданий контакт для роботодавця / програми"""
    __tablename__ = "partner_leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("user_profiles.id"), nullable=False)
    opportunity_id = Column(String(64), ForeignKey("opportunities.id"), nullable=False)
    contact_channel = Column(String(128), nullable=False) # "Telegram @user" або телефон
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile", back_populates="leads")
    opportunity = relationship("Opportunity", back_populates="leads")


class KnowledgeBaseItem(Base):
    """Перевірена база знань для юридичного AI-асистента"""
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String(128), nullable=False) # "Статус УБД", "Виплати за поранення", "Пільги Львів"
    summary = Column(Text, nullable=False)
    official_source = Column(String(512), nullable=False)
    contacts = Column(String(255), nullable=True)
