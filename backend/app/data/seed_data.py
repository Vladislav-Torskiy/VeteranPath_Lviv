"""
Верифіковані дані для Львівщини та всеукраїнських програм
"""

INITIAL_ROADMAP_STEPS = [
    # Етап: Перший тиждень (week_1)
    {
        "id": "step-demob-order",
        "title": "Отримати витяг з наказу про виключення зі списків частини",
        "stage": "week_1",
        "priority": 1,
        "category": "documents",
        "short_description": "Базовий документ, що підтверджує факт звільнення зі служби. Потрібен для всіх подальших виплат і пільг.",
        "required_documents": ["Військовий квиток або посвідчення офіцера", "Припис військової частини"],
        "where_to_go": "Стройова частина / ТЦК та СП за місцем реєстрації у Львові",
        "estimated_time": "1-3 дні",
        "official_source": "Закон України «Про військовий обов'язок і військову службу»",
        "last_verified_at": "2025-01-10",
        "condition_status": [],
        "condition_health": [],
        "condition_goal": []
    },
    {
        "id": "step-tck-registration",
        "title": "Стати на військовий облік у районному ТЦК та СП",
        "stage": "week_1",
        "priority": 1,
        "category": "documents",
        "short_description": "Обов'язкова процедура протягом 5 днів після прибуття до місця проживання для внесення в реєстр «Оберіг».",
        "required_documents": ["Паспорт громадянина України", "Військовий квиток", "Припис"],
        "where_to_go": "Районний ТЦК та СП (Галицько-Франківський, Сихівський, Шевченківський тощо)",
        "estimated_time": "1 день",
        "official_source": "Постанова КМУ №1487",
        "last_verified_at": "2025-01-10",
        "condition_status": [],
        "condition_health": [],
        "condition_goal": []
    },
    {
        "id": "step-ubd-grant",
        "title": "Оформити посвідчення Учасника бойових дій (УБД)",
        "stage": "week_1",
        "priority": 1,
        "category": "documents",
        "short_description": "Якщо комісія частини не видала статус автоматично, подати заяву самостійно через ЦНАП або комісію Міноборони.",
        "required_documents": ["Довідка про безпосередню участь у бойових діях (Додаток 6)", "Витяги з бойових наказів", "2 фото 3х4"],
        "where_to_go": "Будь-який ЦНАП м. Львова або Ветеранський простір (вул. Костя Левицького, 67)",
        "estimated_time": "30 календарних днів",
        "official_source": "Постанова КМУ №413 (зі змінами)",
        "last_verified_at": "2025-01-12",
        "condition_status": ["ubd", "active_duty"],
        "condition_health": [],
        "condition_goal": []
    },
    {
        "id": "step-unbroken-consultation",
        "title": "Первинний скринінг у Національному реабілітаційному центрі «Незламні» (UNBROKEN)",
        "stage": "week_1",
        "priority": 1,
        "category": "health",
        "short_description": "Комплексний огляд фізичного стану, складання індивідуального плану фізіотерапії, відновлення опорно-рухового апарату.",
        "required_documents": ["Виписний епікриз госпіталю", "Паспорт", "Направлення лікаря (за наявності)"],
        "where_to_go": "Центр UNBROKEN, Перше ТМО Львова (вул. І. Миколайчука, 9)",
        "estimated_time": "1-2 дні",
        "official_source": "Львівська міська рада / Програма UNBROKEN",
        "last_verified_at": "2025-01-15",
        "condition_status": [],
        "condition_health": ["rehab_needed", "prosthetics_needed"],
        "condition_goal": []
    },
    {
        "id": "step-superhumans-prosthetics",
        "title": "Реєстрація на високофункціональне протезування в Superhumans Center",
        "stage": "week_1",
        "priority": 1,
        "category": "health",
        "short_description": "Безкоштовна програма біонічного протезування кінцівок та реконструктивної хірургії для ветеранів.",
        "required_documents": ["Медичні документи щодо ампутації/травми", "Паспорт", "Довідка про обставини травми (форма 100/обставини)"],
        "where_to_go": "Superhumans Center (м. Винники, Львівська область)",
        "estimated_time": "Запис онлайн або візит до центру",
        "official_source": "Меморандум МОЗ та Superhumans",
        "last_verified_at": "2025-01-15",
        "condition_status": [],
        "condition_health": ["prosthetics_needed"],
        "condition_goal": []
    },

    # Етап: Перший місяць (month_1)
    {
        "id": "step-financial-support-lviv",
        "title": "Оформити одноразову міську матеріальну допомогу від Львівської міськради",
        "stage": "month_1",
        "priority": 1,
        "category": "finances",
        "short_description": "Виплата захисникам та захисницям, які отримали поранення/інвалідність, згідно з Комплексною програмою підтримки м. Львова.",
        "required_documents": ["Заява", "Копія паспорта та РНОКПП", "Копія довідки МСЕК / ВЛК", "Реквізити банківського рахунку (IBAN)"],
        "where_to_go": "Управління соціального захисту ЛМР або ЦНАП м. Львова",
        "estimated_time": "14-20 днів",
        "official_source": "Рішення виконкому Львівської міської ради",
        "last_verified_at": "2025-01-10",
        "condition_status": ["ubd", "disability"],
        "condition_health": [],
        "condition_goal": []
    },
    {
        "id": "step-msek-disability",
        "title": "Проходження МСЕК (Експертної комісії) для встановлення групи інвалідності",
        "stage": "month_1",
        "priority": 2,
        "category": "health",
        "short_description": "Встановлення ступеня втрати працездатності внаслідок поранення під час захисту Батьківщини (для отримання одноразової грошової допомоги ОГД).",
        "required_documents": ["Направлення форми 088/о", "Постанова ВЛК про причинний зв'язок", "Військовий квиток"],
        "where_to_go": "Львівський обласний центр медико-соціальної експертизи",
        "estimated_time": "2-4 тижні",
        "official_source": "Закон України «Про соціальний і правовий захист військовослужбовців»",
        "last_verified_at": "2025-01-08",
        "condition_status": ["disability"],
        "condition_health": ["rehab_needed", "prosthetics_needed"],
        "condition_goal": []
    },
    {
        "id": "step-utilities-discount",
        "title": "Оформити 75% або 100% знижку на житлово-комунальні послуги",
        "stage": "month_1",
        "priority": 2,
        "category": "finances",
        "short_description": "Пільга на оплату газу, електроенергії, квартплати та опалення для УБД (75%) або осіб з інвалідністю внаслідок війни (100%).",
        "required_documents": ["Посвідчення УБД/інваліда війни", "Паспорт", "Довідка про склад сім'ї", "Номер особових рахунків у комунальних службах"],
        "where_to_go": "Сервісний центр Пенсійного фонду України у Львівській області або портал Дія",
        "estimated_time": "10-14 днів",
        "official_source": "Закон України «Про статус ветеранів війни, гарантії їх соціального захисту»",
        "last_verified_at": "2025-01-10",
        "condition_status": ["ubd", "disability"],
        "condition_health": [],
        "condition_goal": []
    },
    {
        "id": "step-mental-health-support",
        "title": "Безоплатна психологічна реінтеграція та супровід ментора",
        "stage": "month_1",
        "priority": 2,
        "category": "health",
        "short_description": "Сесії з кризовими військовими психологами у комфортному форматі (індивідуально або групи підтримки «Рівний-Рівному»).",
        "required_documents": ["Без документів, лише бажання та контактний зв'язок"],
        "where_to_go": "Ветеранський простір (м. Львів, вул. Костя Левицького, 67) або Лінія підтримки 1545",
        "estimated_time": "У день звернення",
        "official_source": "Міністерство у справах ветеранів України",
        "last_verified_at": "2025-01-15",
        "condition_status": [],
        "condition_health": ["psychological", "rehab_needed", "none"],
        "condition_goal": []
    },

    # Етап: 3 місяці (month_3)
    {
        "id": "step-dcz-voucher",
        "title": "Отримати ваучер на безкоштовне навчання (до 30 280 грн) від Держслужби зайнятості",
        "stage": "month_3",
        "priority": 1,
        "category": "career",
        "short_description": "Держава повністю оплачує перекваліфікацію або отримання нової професії (IT, логістика, водій спецтехніки, кібербезпека, психологія).",
        "required_documents": ["Посвідчення УБД", "Паспорт", "Трудова книжка (за наявності)", "Диплом про освіту"],
        "where_to_go": "Львівський міський центр зайнятості (вул. Княгині Ольги, 122) або онлайн на dcz.gov.ua",
        "estimated_time": "3-5 робочих днів",
        "official_source": "Постанова КМУ №207",
        "last_verified_at": "2025-01-14",
        "condition_status": ["ubd", "disability"],
        "condition_health": [],
        "condition_goal": ["work", "education"]
    },
    {
        "id": "step-veteran-business-grant",
        "title": "Подати заявку на грант «єРобота: Власна справа для ветеранів» (до 1 000 000 грн)",
        "stage": "month_3",
        "priority": 1,
        "category": "business",
        "short_description": "Безповоротний державний грант для ветеранів та їхнього подружжя: 250 тис. грн (1 робоче місце), 500 тис. грн (2 місця) або 1 млн грн для ФОП від 36 місяців.",
        "required_documents": ["Бізнес-план", "Заявка через портал Дія", "Довідка про відсутність податкового боргу"],
        "where_to_go": "Портал Дія + співбесіда у Львівському Ощадбанку",
        "estimated_time": "15-20 робочих днів",
        "official_source": "Постанова КМУ №738",
        "last_verified_at": "2025-01-15",
        "condition_status": ["ubd", "disability", "family_member"],
        "condition_health": [],
        "condition_goal": ["business"]
    },
    {
        "id": "step-cv-translation-job",
        "title": "Адаптувати резюме через VeteranPath та пройти ветеранську співбесіду",
        "stage": "month_3",
        "priority": 2,
        "category": "career",
        "short_description": "Сформувати резюме цивільною мовою у модулі «Мій досвід» та відгукнутися на верифіковані вакансії львівських партнерів.",
        "required_documents": ["Сформоване резюме у додатку"],
        "where_to_go": "Розділ «Вакансії та програми» у VeteranPath",
        "estimated_time": "1 день",
        "official_source": "Платформа VeteranPath Lviv",
        "last_verified_at": "2025-01-15",
        "condition_status": [],
        "condition_health": [],
        "condition_goal": ["work"]
    },

    # Етап: Довгостроково (long_term)
    {
        "id": "step-ye-oselya",
        "title": "Оформити пільгову іпотеку «єОселя» під 3% річних",
        "stage": "long_term",
        "priority": 2,
        "category": "finances",
        "short_description": "Державна програма доступного кредитування житла під фіксовані 3% для ветеранів та членів їхніх сімей.",
        "required_documents": ["Заява через Дію", "Довідка про доходи сім'ї", "Посвідчення УБД"],
        "where_to_go": "Мобільний застосунок Дія (розділ єОселя)",
        "estimated_time": "Від 10 днів",
        "official_source": "ПрАТ «Укрфінжитло» / Дія",
        "last_verified_at": "2025-01-12",
        "condition_status": ["ubd", "disability"],
        "condition_health": [],
        "condition_goal": []
    },
    {
        "id": "step-veteran-hub-community",
        "title": "Приєднатися до Ветеранської спільноти підприємців Львівщини",
        "stage": "long_term",
        "priority": 3,
        "category": "business",
        "short_description": "Нетворкінг, обмін досвідом, участь у ярмарках ветеранських бізнесів та спільні муніципальні закупівлі.",
        "required_documents": ["Реєстрація ФОП / ТОВ або статус ветерана"],
        "where_to_go": "Львівський центр підтримки підприємництва (пл. Ринок, 1)",
        "estimated_time": "За графіком подій",
        "official_source": "Львівська міська рада",
        "last_verified_at": "2025-01-15",
        "condition_status": [],
        "condition_health": [],
        "condition_goal": ["business"]
    }
]

INITIAL_OPPORTUNITIES = [
    {
        "id": "opp-softserve-ops",
        "partner_id": "part-softserve",
        "partner_name": "SoftServe Veterans Program",
        "title": "Junior Logistics & IT Operations Coordinator",
        "type": "vacancy",
        "category": "IT",
        "location": "Львів (гібридний формат)",
        "description": "Координація апаратного забезпечення, внутрішньої логістики та технічної підтримки команд. Програма ветеранського менторства, супровід психолога.",
        "benefits": "Медичне страхування з покриттям реабілітації, ментор з досвідом служби, гнучкий графік",
        "salary_range": "35 000 - 45 000 грн",
        "contact_url": "https://softserveinc.com/careers"
    },
    {
        "id": "opp-meest-fleet-lead",
        "partner_id": "part-meest",
        "partner_name": "Meest Пошта Львів",
        "title": "Керівник зміни логістичного хабу / Диспетчер",
        "type": "vacancy",
        "category": "logistics",
        "location": "Львів (вул. Зелена)",
        "description": "Управління зміною водіїв та сортувальників, оперативний облік відправлень, контроль термінів. Ідеально підходить для командирів відділень та взводів.",
        "benefits": "Офіційне бронювання згідно закону, адаптаційний період, премії за ефективність",
        "salary_range": "38 000 - 50 000 грн",
        "contact_url": "https://meest.com"
    },
    {
        "id": "opp-kormotech-tech",
        "partner_id": "part-kormotech",
        "partner_name": "Кормотех (Kormotech)",
        "title": "Оператор автоматизованих виробничих ліній",
        "type": "vacancy",
        "category": "production",
        "location": "с. Прилбичі (безкоштовний довіз зі Львова)",
        "description": "Обслуговування сучасного виробничого обладнання, моніторинг показників приладів. Навчання з нуля на робочому місці.",
        "benefits": "Повне соцзабезпечення, харчування, реабілітаційний пакет підтримки",
        "salary_range": "30 000 - 40 000 грн",
        "contact_url": "https://kormotech.com"
    },
    {
        "id": "opp-ucu-leadership-course",
        "partner_id": "part-ucu",
        "partner_name": "Бізнес-школа УКУ (LvBS)",
        "title": "Курс «Лідерство та управління бізнес-проектами для ветеранів»",
        "type": "course",
        "category": "business",
        "location": "Львів (кампус УКУ, вул. Козельницька)",
        "description": "100% стипендійна програма: фінанси, операційний менеджмент, маркетинг, юридична база для запуску власної справи.",
        "benefits": "Повна стипендія від донорів, персональний ментор-підприємець",
        "salary_range": "Безкоштовно (грант)",
        "contact_url": "https://lvbs.top"
    },
    {
        "id": "opp-lviv-it-cluster-qa",
        "partner_id": "part-it-cluster",
        "partner_name": "Lviv IT Cluster Academy",
        "title": "Інтенсив: Manual & Automated QA Engineer",
        "type": "course",
        "category": "IT",
        "location": "Львів (онлайн + воркшопи)",
        "description": "3-місячний практичний курс тестування програмного забезпечення з гарантованими співбесідами у компаніях-членах кластеру.",
        "benefits": "Покривається ваучером Центру зайнятості або стипендією кластеру",
        "salary_range": "Безкоштовно для УБД",
        "contact_url": "https://itcluster.lviv.ua"
    },
    {
        "id": "opp-yerobota-grand-fund",
        "partner_id": "part-yerobota",
        "partner_name": "Дія / Ощадбанк / Львівська ОВА",
        "title": "Грант для ветеранів на відкриття бізнесу до 1 000 000 грн",
        "type": "grant",
        "category": "business",
        "location": "Львівська область",
        "description": "Фінансування обладнання, сировини, оренди та транспорту для ветеранського бізнесу. Супровід експертів ОВА на всіх етапах підготовки бізнес-плану.",
        "benefits": "Безповоротні кошти за умови створення робочих місць",
        "salary_range": "до 1 000 000 грн",
        "contact_url": "https://diia.gov.ua/services/grant-dlya-veteraniv"
    }
]

INITIAL_KNOWLEDGE_BASE = [
    {
        "topic": "Статус УБД та пільги",
        "summary": "Статус учасника бойових дій (УБД) надає право на 75% знижку на ЖКП, безкоштовний проїзд міським та приміським транспортом, першочергове медичне обслуговування, отримання безоплатних ліків за рецептом та ваучерів на навчання.",
        "official_source": "Закон України «Про статус ветеранів війни, гарантії їх соціального захисту» ст. 12",
        "contacts": "Гаряча лінія Мінветеранів: 1545 (кнопка 9)"
    },
    {
        "topic": "Реабілітація у Львові (Unbroken / Superhumans)",
        "summary": "У Львові діють два провідні національні центри: UNBROKEN (Перше ТМО Львова, вул. Миколайчука, 9) — медична, фізична та психологічна реабілітація; Superhumans Center (Винники) — протезування, відновлення слуху, пластична хірургія та ментальне здоров'я. Послуги для військових та ветеранів є повністю безоплатними.",
        "official_source": "Львівська міська рада / UNBROKEN Ukraine",
        "contacts": "Контакт-центр UNBROKEN: 0 800 333 003"
    },
    {
        "topic": "Одноразова грошова допомога при пораненні",
        "summary": "Розмір одноразової грошової допомоги (ОГД) залежить від встановленої групи інвалідності або відсотка втрати працездатності: I група — 400 прожиткових мінімумів, II група — 300, III група — 250. При втраті працездатності без групи — від 50 до 100 прожиткових мінімумів.",
        "official_source": "Постанова КМУ №975 від 25 грудня 2013 р.",
        "contacts": "Гаряча лінія юридичної сотні: 0 800 308 100"
    },
    {
        "topic": "Гранти на власну справу «єРобота»",
        "summary": "Учасники бойових дій та їхні дружини/чоловіки можуть отримати грант: 250 тис. грн (створення 1 робочого місця), 500 тис. грн (2 місця, співфінансування 70/30), 1 млн грн (4 місця, статус ФОП від 3 років). Подання через Дію.",
        "official_source": "Постанова Кабінету Міністрів України №738",
        "contacts": "Ощадбанк Ветеранський консалтинг: 0 800 210 800"
    }
]
