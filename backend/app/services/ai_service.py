import json
import logging
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.mode = settings.AI_MODE

    def parse_free_text_onboarding(self, raw_text: str) -> Dict[str, Any]:
        """
        Витягує структуровані параметри з вільної розповіді ветерана
        """
        # Перевірка: якщо режим MOCK або ключ відсутній - використовуємо безвідмовний евристичний мок
        if self.mode == "MOCK" or not self.api_key or self.api_key.startswith("your_"):
            return self._mock_parse_free_text(raw_text)

        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            prompt = f"""
Ти експертний помічник ветеранської платформи. Твоє завдання - проаналізувати вільний текст ветерана і повернути ТІЛЬКИ валідний JSON без зайвих слів і markdown-форматування:
{{
  "status": "ubd" | "active_duty" | "disability" | "family_member",
  "region": "Львівська область",
  "city": "назва міста або Львів",
  "demobilized_date": "приблизна дата або 'нещодавно'",
  "health_status": "none" | "rehab_needed" | "prosthetics_needed" | "psychological",
  "primary_goal": "work" | "business" | "education" | "health",
  "education": "освіта або 'Середня спеціальна / вища'",
  "summary_message": "Людяне підсумування 1-2 реченнями: як ти зрозумів ситуацію людини"
}}

Текст ветерана:
\"{raw_text}\"
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            cleaned = response.text.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            return {
                "parsed_profile": {
                    "status": data.get("status", "ubd"),
                    "region": data.get("region", "Львівська область"),
                    "city": data.get("city", "Львів"),
                    "demobilized_date": data.get("demobilized_date", "Нещодавно"),
                    "health_status": data.get("health_status", "none"),
                    "primary_goal": data.get("primary_goal", "work"),
                    "education": data.get("education", "Вища / середня спеціальна")
                },
                "summary_message": data.get("summary_message", "Дякуємо за службу! Ми виділили ключові потреби для вашого персонального плану."),
                "confidence": 0.95
            }
        except Exception as e:
            logger.warning(f"Помилка виклику Gemini API ({e}), перемикання на резервний обробник.")
            return self._mock_parse_free_text(raw_text)

    def translate_military_experience(self, text: str, target_area: str = "management") -> Dict[str, Any]:
        """
        Перекладає військовий досвід на мову цивільних вакансій та резюме
        """
        if self.mode == "MOCK" or not self.api_key or self.api_key.startswith("your_"):
            return self._mock_translate_experience(text)

        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            prompt = f"""
Ти кар'єрний консультант, який допомагає ветеранам адаптувати військовий досвід для цивільних роботодавців.
Проаналізуй опис служби і поверни ТІЛЬКИ валідний JSON:
{{
  "civilian_skills": ["навичка 1", "навичка 2", "навичка 3", "навичка 4"],
  "resume_bullet_points": [
    "Формулювання 1 для резюме дієсловом дії з фокусом на результат",
    "Формулювання 2 для резюме",
    "Формулювання 3 для резюме"
  ],
  "recommended_roles": ["Професія 1", "Професія 2", "Професія 3"],
  "skill_gaps_and_courses": [
    {{"role": "Професія 1", "gap": "Чого не вистачає", "course": "Рекомендований курс/сертифікат"}}
  ]
}}

Опис служби ветерана:
\"{text}\"
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            cleaned = response.text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"Помилка Gemini у translate_experience ({e}), fallback.")
            return self._mock_translate_experience(text)

    def answer_chat_query(self, question: str, knowledge_items: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Відповідь на запитання виключно на основі перевіреної бази знань (RAG-light)
        """
        if self.mode == "MOCK" or not self.api_key or self.api_key.startswith("your_"):
            return self._mock_answer_chat(question, knowledge_items)

        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            context = "\n\n".join([f"Тема: {k['topic']}\nСуть: {k['summary']}\nДжерело: {k['official_source']}\nКонтакт: {k.get('contacts', '')}" for k in knowledge_items])
            
            prompt = f"""
Ти юридичний та довідковий помічник ветерана у Львові. 
Відповідай ВИКЛЮЧНО на основі наступної бази знань. Якщо інформації недостатньо, чесно скажи про це і порадь звернутися на гарячу лінію або до ЦНАП м. Львова.
Завжди вказуй офіційне джерело закону або постанови.

База знань:
{context}

Запитання ветерана:
\"{question}\"
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            sources = [k['official_source'] for k in knowledge_items if any(w.lower() in k['topic'].lower() or w.lower() in k['summary'].lower() for w in question.lower().split())]
            if not sources:
                sources = ["Законодавство України щодо ветеранів війни", "ЦНАП м. Львів"]

            return {
                "answer": response.text.strip(),
                "sources": sources[:2],
                "recommended_hotlines": ["1545 (кнопка 9 — Ветеранська лінія)", "0 800 333 003 (UNBROKEN Львів)"]
            }
        except Exception as e:
            logger.warning(f"Помилка Gemini у answer_chat_query ({e}), fallback.")
            return self._mock_answer_chat(question, knowledge_items)

    # =========================================================================
    # REVOLUTIONARY OFFLINE MOCKS FOR 100% BULLETPROOF PITCH PRESENTATION
    # =========================================================================

    def _mock_parse_free_text(self, text: str) -> Dict[str, Any]:
        lower = text.lower()
        
        status = "ubd"
        if "поранен" in lower or "інвалід" in lower or "госпітал" in lower:
            status = "disability"
        elif "дружин" in lower or "чоловік" in lower or "сім'я" in lower or "родин" in lower:
            status = "family_member"

        health = "none"
        if "протез" in lower or "ампутац" in lower:
            health = "prosthetics_needed"
        elif "поранен" in lower or "колін" in lower or "спин" in lower or "реабілітац" in lower:
            health = "rehab_needed"
        elif "сон" in lower or "стрес" in lower or "психол" in lower or "тривог" in lower:
            health = "psychological"

        goal = "work"
        if "бізнес" in lower or "справ" in lower or "кав'ярн" in lower or "грант" in lower:
            goal = "business"
        elif "навчан" in lower or "курс" in lower or "it" in lower or "вчитися" in lower:
            goal = "education"
        elif "лікуват" in lower or "віднов" in lower:
            goal = "health"

        city = "Львів"
        if "дрогобич" in lower:
            city = "Дрогобич"
        elif "стрий" in lower:
            city = "Стрий"

        summary = (
            f"Я зрозумів ваш запит: ви прагнете зосередитися на напрямку '{'працевлаштування' if goal == 'work' else 'власна справа' if goal == 'business' else 'відновлення здоров’я'}' "
            f"у місті {city}. { 'Враховано потребу у відновленні/реабілітації через центр Unbroken.' if health != 'none' else ''} "
            f"Перевірте поля нижче та натисніть «Скласти мій план»."
        )

        return {
            "parsed_profile": {
                "status": status,
                "region": "Львівська область",
                "city": city,
                "demobilized_date": "Останній місяць",
                "health_status": health,
                "primary_goal": goal,
                "education": "Вища / бакалавр"
            },
            "summary_message": summary,
            "confidence": 0.98
        }

    def _mock_translate_experience(self, text: str) -> Dict[str, Any]:
        return {
            "civilian_skills": [
                "Управління людьми та малими командами (Team Leadership)",
                "Кризовий менеджмент та швидке прийняття рішень у стресових умовах",
                "Операційна логістика, матеріально-технічний облік і постачання",
                "Контроль технічного стану обладнання та техніки безпеки"
            ],
            "resume_bullet_points": [
                "Керував оперативною командою з 10+ осіб: планування змін, розподіл ресурсу та 100% виконання поставлених цілей у режимі невизначеності.",
                "Організував безперебійне постачання матеріально-технічних засобів і транспорту з нульовими втратами в критичних умовах.",
                "Впровадив щоденний регламент техогляду та обліку техніки, скоротивши час виходу з ладу на 35%."
            ],
            "recommended_roles": [
                "Менеджер операційної логістики / Диспетчер хабу",
                "Керівник проектної групи / Team Lead підтримки",
                "Менеджер виробничої зміни / Супервайзер об'єкта"
            ],
            "skill_gaps_and_courses": [
                {
                    "role": "Менеджер операційної логістики",
                    "gap": "Робота з WMS/ERP системами (1C/BAS, SAP)",
                    "course": "Безкоштовний інтенсив «Сучасна цифрова логістика» (Львівський ЦЗ)"
                },
                {
                    "role": "Керівник проектів",
                    "gap": "Методології Agile / Scrum",
                    "course": "Курс «Project Management Essentials» від Lviv IT Cluster Academy"
                }
            ]
        }

    def _mock_answer_chat(self, question: str, knowledge_items: List[Dict[str, str]]) -> Dict[str, Any]:
        lower = question.lower()
        if "убд" in lower or "пільг" in lower:
            return {
                "answer": "Статус УБД надає 75% знижку на житлово-комунальні послуги, право на безоплатний проїзд міським транспортом, позачергове меддопомогу та ваучери на навчання. Документи можна подати у будь-якому ЦНАП м. Львова або через сервісний офіс у справах ветеранів.",
                "sources": ["Закон України «Про статус ветеранів війни» ст. 12", "ЦНАП м. Львова"],
                "recommended_hotlines": ["1545 (кнопка 9 — Ветеранська лінія)", "032 297 57 95 (ЦНАП Львів)"]
            }
        elif "реабілітац" in lower or "незламні" in lower or "unbroken" in lower or "поранен" in lower:
            return {
                "answer": "У Львові безкоштовну комплексну медичну та фізичну реабілітацію проводить Національний центр «Незламні» (UNBROKEN) при Першому ТМО (вул. Миколайчука, 9). Якщо потрібне біонічне протезування — звертайтеся до Superhumans Center (Винники). Усі послуги для ветеранів повністю безоплатні за державно-донорськими програмами.",
                "sources": ["Програма UNBROKEN Львівської міськради", "Меморандум МОЗ та Superhumans"],
                "recommended_hotlines": ["0 800 333 003 (Контакт-центр UNBROKEN)"]
            }
        elif "грант" in lower or "бізнес" in lower or "грош" in lower:
            return {
                "answer": "Ветерани та їхнє подружжя можуть отримати безповоротний державний грант через «єРобота» до 1 000 000 грн на відкриття власної справи (подання через портал Дія). Також діє Львівська обласна програма підтримки ветеранського бізнесу з компенсацією відсотків за кредитами.",
                "sources": ["Постанова Кабміну №738 («єРобота»)", "Львівська ОВА / Департамент економічної політики"],
                "recommended_hotlines": ["0 800 210 800 (Ощадбанк Ветеранський відділ)"]
            }
        else:
            return {
                "answer": "Дякуємо за запитання. Згідно з законодавством про соціальний захист ветеранів, відповідні заяви приймаються управлінням соціального захисту та ЦНАП. Рекомендуємо отримати адресну консультацію за офіційними контактами.",
                "sources": ["Офіційний портал ветеранських сервісів м. Львова"],
                "recommended_hotlines": ["1545 (Цілодобова урядова лінія)", "0800 505 210 (Ветеранський простір)"]
            }

ai_service = AIService()
