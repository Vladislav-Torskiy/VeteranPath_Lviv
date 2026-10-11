"use client";

import { useState, useEffect } from "react";
import { 
  Building2, Users, HeartHandshake, TrendingUp, PieChart, 
  ShieldAlert, MessageSquare, Bot 
} from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function PartnerView() {
  const [data, setData] = useState<any>(null);
  const [feedbacks, setFeedbacks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
    loadFeedbacks();
  }, []);

  const loadAnalytics = async () => {
    try {
      const res = await fetchApi("/partner/analytics");
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadFeedbacks = async () => {
    try {
      const res = await fetchApi("/feedback/list");
      setFeedbacks(res);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500 text-sm">Завантаження аналітики кабінету...</div>;
  }

  const stats = data?.stats || {
    total_veterans_registered: 0,
    total_leads_generated: 0,
    active_opportunities: 0,
    feedback_count: 0
  };

  const needs = data?.community_needs || {
    rehab_needed: 0,
    goal_work: 0,
    goal_business: 0,
    goal_education: 0
  };

  const totalNeeds = Math.max(stats.total_veterans_registered, 1);

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-fade-in px-2 sm:px-0">
      {/* Шапка B2B / B2G */}
      <div className="bg-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold uppercase tracking-wider">
              Екосистема партнерства & GovTech
            </span>
            <h2 className="text-xl sm:text-3xl font-extrabold mt-2">Кабінет Роботодавця та Муніципалітету</h2>
            <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
              Чесна аналітика в реальному часі без штучних накруток: реальні потреби ветеранів Львівщини, відгуки на вакансії та інтеграція з Telegram-ботом партнерів.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Live База даних
            </span>
            <div className="px-3 py-1.5 rounded-xl bg-purple-900/40 border border-purple-500/40 text-xs font-semibold text-purple-300 flex items-center gap-1.5">
              <Bot className="w-3.5 h-3.5" />
              Telegram-бот активний
            </div>
          </div>
        </div>

        {/* Чесні Метрики без накруток */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mt-6 pt-6 border-t border-slate-800">
          <div className="bg-slate-800/60 p-4 rounded-2xl border border-slate-700/60">
            <div className="flex items-center gap-1.5 text-slate-400 text-xs font-medium">
              <Users className="w-3.5 h-3.5 text-emerald-400" /> Ветеранів у базі
            </div>
            <div className="text-2xl sm:text-3xl font-black text-white mt-1">
              {stats.total_veterans_registered}
            </div>
          </div>

          <div className="bg-slate-800/60 p-4 rounded-2xl border border-slate-700/60">
            <div className="flex items-center gap-1.5 text-slate-400 text-xs font-medium">
              <HeartHandshake className="w-3.5 h-3.5 text-emerald-400" /> Відгуків (Лідів)
            </div>
            <div className="text-2xl sm:text-3xl font-black text-emerald-400 mt-1">
              {stats.total_leads_generated}
            </div>
          </div>

          <div className="bg-slate-800/60 p-4 rounded-2xl border border-slate-700/60">
            <div className="flex items-center gap-1.5 text-slate-400 text-xs font-medium">
              <Building2 className="w-3.5 h-3.5 text-emerald-400" /> Активних програм
            </div>
            <div className="text-2xl sm:text-3xl font-black text-white mt-1">
              {stats.active_opportunities}
            </div>
          </div>

          <div className="bg-slate-800/60 p-4 rounded-2xl border border-slate-700/60">
            <div className="flex items-center gap-1.5 text-slate-400 text-xs font-medium">
              <MessageSquare className="w-3.5 h-3.5 text-amber-400" /> Зауважень/Відгуків
            </div>
            <div className="text-2xl sm:text-3xl font-black text-amber-300 mt-1">
              {stats.feedback_count || feedbacks.length}
            </div>
          </div>
        </div>
      </div>

      {/* GovTech Аналітика потреб громади Львівщини */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
          <h3 className="font-bold text-slate-900 text-base flex items-center gap-2 mb-2">
            <PieChart className="w-5 h-5 text-emerald-600" />
            Теплова карта потреб ветеранів Львівщини (Real-time)
          </h3>
          <p className="text-xs text-slate-500 mb-5">
            Формується на основі опитувальника та профілів ветеранів для координації ресурсів громади:
          </p>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                <span>Потреба у роботі / кар'єрі</span>
                <span className="text-slate-900 font-bold">{needs.goal_work} ветеранів</span>
              </div>
              <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-slate-900 rounded-full transition-all duration-500" 
                  style={{ width: `${stats.total_veterans_registered > 0 ? (needs.goal_work / totalNeeds) * 100 : 0}%` }} 
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                <span>Потреба у фізичній реабілітації (UNBROKEN / Superhumans)</span>
                <span className="text-slate-900 font-bold">{needs.rehab_needed} ветеранів</span>
              </div>
              <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-emerald-600 rounded-full transition-all duration-500" 
                  style={{ width: `${stats.total_veterans_registered > 0 ? (needs.rehab_needed / totalNeeds) * 100 : 0}%` }} 
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                <span>Власна справа / Гранти «єРобота»</span>
                <span className="text-slate-900 font-bold">{needs.goal_business} ветеранів</span>
              </div>
              <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-purple-600 rounded-full transition-all duration-500" 
                  style={{ width: `${stats.total_veterans_registered > 0 ? (needs.goal_business / totalNeeds) * 100 : 0}%` }} 
                />
              </div>
            </div>
          </div>
        </div>

        {/* Останні відгуки на вакансії */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-base flex items-center gap-2 mb-1">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              Останні відгуки ветеранів на вакансії
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Кандидати, які надали добровільну згоду на зв'язок:
            </p>

            <div className="divide-y divide-slate-100 text-xs">
              {data?.recent_leads && data.recent_leads.length > 0 ? (
                data.recent_leads.map((lead: any) => (
                  <div key={lead.id} className="py-2.5 flex items-center justify-between">
                    <div>
                      <strong className="text-slate-900 block">{lead.opportunity_title}</strong>
                      <span className="text-slate-500">{lead.partner_name}</span>
                    </div>
                    <div className="text-right">
                      <span className="font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                        {lead.contact_channel}
                      </span>
                      <span className="text-[10px] text-slate-400 block mt-0.5">{lead.created_at}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="py-8 text-center text-slate-400 text-xs">
                  Поки що відгуків немає. Пройдіть тестовий шлях ветерана у розділі Вакансій, щоб з'явився перший лід!
                </div>
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 text-[11px] text-slate-400 flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5 text-slate-500" />
            Дані передаються суворо згідно з політикою згоди ветерана.
          </div>
        </div>
      </div>

      {/* Панель адміністратора: Зауваження та пропозиції */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <div>
            <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-amber-600" />
              Зауваження та відгуки (Сайт + Telegram-бот)
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Всі звернення від ветеранів та партнерів для адміністратора платформи:
            </p>
          </div>
          <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-amber-100 text-amber-900">
            {feedbacks.length} повідомлень
          </span>
        </div>

        <div className="space-y-3">
          {feedbacks.length > 0 ? (
            feedbacks.map((item) => (
              <div key={item.id} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs space-y-1">
                <div className="flex items-center justify-between text-slate-500">
                  <span className="font-bold text-slate-800">
                    {item.sender_name || "Користувач"} {item.sender_contact ? `(${item.sender_contact})` : ""}
                  </span>
                  <span className="text-[10px]">Джерело: <strong className="text-slate-700">{item.source}</strong> | {item.created_at}</span>
                </div>
                <p className="text-slate-700 text-xs pt-1 leading-relaxed">{item.message}</p>
              </div>
            ))
          ) : (
            <div className="text-center py-6 text-slate-400 text-xs">
              Зауважень ще не надходило. Скористайтеся кнопкою «Відгук» у шапці, щоб протестувати надсилання!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
