from sqlalchemy.orm import Session
from app.models.entities import RoadmapStep, Opportunity, KnowledgeBaseItem
from app.data.seed_data import INITIAL_ROADMAP_STEPS, INITIAL_OPPORTUNITIES, INITIAL_KNOWLEDGE_BASE

def seed_database_if_empty(db: Session):
    # Кроки
    if db.query(RoadmapStep).count() == 0:
        for s in INITIAL_ROADMAP_STEPS:
            step = RoadmapStep(
                id=s["id"],
                title=s["title"],
                stage=s["stage"],
                priority=s["priority"],
                category=s["category"],
                short_description=s["short_description"],
                required_documents=s["required_documents"],
                where_to_go=s["where_to_go"],
                estimated_time=s["estimated_time"],
                official_source=s["official_source"],
                last_verified_at=s["last_verified_at"],
                condition_status=s["condition_status"],
                condition_health=s["condition_health"],
                condition_goal=s["condition_goal"]
            )
            db.add(step)
    
    # Можливості та вакансії
    if db.query(Opportunity).count() == 0:
        for opp in INITIAL_OPPORTUNITIES:
            item = Opportunity(
                id=opp["id"],
                partner_id=opp["partner_id"],
                partner_name=opp["partner_name"],
                title=opp["title"],
                type=opp["type"],
                category=opp["category"],
                location=opp["location"],
                description=opp["description"],
                benefits=opp.get("benefits"),
                salary_range=opp.get("salary_range"),
                contact_url=opp.get("contact_url")
            )
            db.add(item)

    # База знань
    if db.query(KnowledgeBaseItem).count() == 0:
        for kb in INITIAL_KNOWLEDGE_BASE:
            item = KnowledgeBaseItem(
                topic=kb["topic"],
                summary=kb["summary"],
                official_source=kb["official_source"],
                contacts=kb.get("contacts")
            )
            db.add(item)

    db.commit()
