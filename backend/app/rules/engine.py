from typing import List, Dict, Any
from app.models.entities import RoadmapStep, UserProfile

STAGE_TITLES = {
    "week_1": "Перший тиждень: Документи та першочерговий захист",
    "month_1": "Перший місяць: Виплати, оцінка здоров'я та пільги",
    "month_3": "3 місяці: Навчання, робота або запуск справи",
    "long_term": "Довгостроково: Житло («єОселя») та ветеранська спільнота"
}

def filter_and_rank_steps(profile: UserProfile, all_steps: List[RoadmapStep], completed_step_ids: set) -> Dict[str, Any]:
    """
    Детермінований рушій правил (Rule Engine):
    Відбирає кроки згідно з юридичним статусом, потребами в реабілітації та цілями ветерана.
    Жодної вигаданої інформації - виключно юридичні факти та перевірені локації.
    """
    selected_steps = []

    for step in all_steps:
        # 1. Перевірка статусу
        if step.condition_status and len(step.condition_status) > 0:
            if profile.status and profile.status not in step.condition_status:
                continue

        # 2. Перевірка здоров'я/реабілітації
        if step.condition_health and len(step.condition_health) > 0:
            if profile.health_status and profile.health_status not in step.condition_health:
                continue

        # 3. Перевірка цілі (робота / бізнес / навчання)
        if step.condition_goal and len(step.condition_goal) > 0:
            if profile.primary_goal and profile.primary_goal not in step.condition_goal:
                continue

        is_completed = step.id in completed_step_ids
        
        step_dict = {
            "id": step.id,
            "title": step.title,
            "stage": step.stage,
            "stage_title": STAGE_TITLES.get(step.stage, step.stage),
            "priority": step.priority,
            "category": step.category,
            "short_description": step.short_description,
            "required_documents": step.required_documents or [],
            "where_to_go": step.where_to_go,
            "estimated_time": step.estimated_time,
            "official_source": step.official_source,
            "last_verified_at": step.last_verified_at,
            "is_completed": is_completed
        }
        selected_steps.append(step_dict)

    # Сортування: спочатку за пріоритетом (1 -> 2 -> 3), далі за стадіями
    stage_order = {"week_1": 1, "month_1": 2, "month_3": 3, "long_term": 4}
    selected_steps.sort(key=lambda s: (stage_order.get(s["stage"], 99), s["priority"]))

    # Групування за етапами
    stages = {}
    for stage_key, stage_title in STAGE_TITLES.items():
        stage_steps = [s for s in selected_steps if s["stage"] == stage_key]
        if stage_steps:
            stages[stage_key] = {
                "title": stage_title,
                "steps": stage_steps
            }

    # Топ-3 найважливіші невиконані кроки
    priority_steps = [s for s in selected_steps if not s["is_completed"] and s["priority"] == 1][:3]
    if len(priority_steps) < 3:
        priority_steps = [s for s in selected_steps if not s["is_completed"]][:3]

    total = len(selected_steps)
    completed = len([s for s in selected_steps if s["is_completed"]])
    pct = int((completed / total) * 100) if total > 0 else 0

    return {
        "total_steps": total,
        "completed_steps": completed,
        "progress_percentage": pct,
        "priority_steps": priority_steps,
        "stages": stages
    }
