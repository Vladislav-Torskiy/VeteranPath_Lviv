"use client";

import { useState, useEffect, useCallback } from "react";
import { 
  Building2, Users, HeartHandshake, TrendingUp, PieChart, 
  ShieldAlert, MessageSquare, Bot, RefreshCw 
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function apiFetch(endpoint: string) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export default function PartnerView() {
  const [data, setData] = useState<any>(null);
  const [feedbacks, setFeedbacks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [analytics, fbs] = await Promise.all([
        apiFetch("/partner/analytics"),
        apiFetch("/feedback/list"),
      ]);
      setData(analytics);
      setFeedbacks(fbs);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Помилка завантаження аналітики:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAll();
    // Автооновлення кожні 30 секунд
    const interval = setInterval(loadAll, 30_000);
    return () => clearInterval(interval);
  }, [loadAll]);

  const stats = data?.stats ?? {
    total_veterans_registered: 0,
    total_leads_generated: 0,
    active_opportunities: 0,
    feedback_count: 0,
  };

  const needs = data?.community_needs ?? {
    rehab_needed: 0,
    goal_work: 0,
    goal_business: 0,
    goal_education: 0,
  };

  const totalNeeds = Math.max(stats.total_veterans_registered, 1);

  return (
    <div className="space-y-6 max-w-6xl mx-auto px-2 sm:px-0">
      {/* Шапка B2B / B2G */}
      <div className="bg-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div>
            <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold uppercase tracking-wider">
              Екосистема партнерства & GovTech
            </span>
            <h2 className="text-xl sm:text-3xl font-extrabold mt-2">Кабінет Роботодавця та Муніципалітету</h2>
            <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
              Реальна аналітика без накруток: потреби ветеранів Львівщини, відгуки на вакансії, інтеграція з Telegram-ботом.
            </p>
          </div>

          <div className="flex flex-col sm:items-end gap-2">
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

            {/* Кнопка оновлення */}
            <button
              onClick={loadAll}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-slate-300 transition disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              {loading ? "Оновлення..." : "Оновити"}
            </button>

            {lastUpdated && (
              <span className="text-[11px] text-slate-500">
                Оновлено: {lastUpdated.toLocaleTimeString("uk-UA")}
              </span>
            )}
          </div>
        </div>

        {/* Метрики */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mt-6 pt-6 border-t border-slate-800">
          {[
            { icon: <Users className="w-3.5 h-3.5 text-emerald-400" />, label: "Ветеранів у базі", value: stats.total_veterans_registered, color: "text-white" },
            { icon: <HeartHandshake className="w-3.5 h-3.5 text-emerald-400" />, label: "Відгуків (Лідів)", value: stats.total_leads_generated, color: "text-emerald-400" },
            { icon: <Building2 className="w-3.5 h-3.5 text-emerald-400" />, label: "Активних програм", value: stats.active_opportunities, color: "text-white" },
            { icon: <MessageSquare className="w-3.5 h-3.5 text-amber-400" />, label: "Зауважень/Відгуків", value: stats.feedback_count || feedbacks.length, color: "text-amber-300" },
          ].map((m) => (
            <div key={m.label} className="bg-slate-800/60 p-4 rounded-2xl border border-slate-700/60">
              <div className="flex items-center gap-1.5 text-slate-400 text-xs font-medium mb-1">
                {m.icon} {m.label}
              </div>
              <div className={`text-2xl sm:text-3xl font-black ${m.color}`}>
                {loading ? "–" : m.value}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Аналітика потреб + Відгуки на вакансії */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Теплова карта потреб */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
          <h3 className="font-bold text-slate-900 text-base flex items-center gap-2 mb-1">
            <PieChart className="w-5 h-5 text-emerald-600" />
            Теплова карта потреб ветеранів Львівщини
          </h3>
          <p className="text-xs text-slate-500 mb-5">На основі реальних профілів для координації ресурсів громади:</p>

          <div className="space-y-4">
            {[
              { label: "Потреба у роботі / кар'єрі", value: needs.goal_work, color: "bg-slate-900" },
              { label: "Потреба у фізичній реабілітації (UNBROKEN / Superhumans)", value: needs.rehab_needed, color: "bg-emerald-600" },
              { label: "Власна справа / Гранти «єРобота»", value: needs.goal_business, color: "bg-purple-600" },
              { label: "Освіта / перекваліфікація", value: needs.goal_education, color: "bg-blue-600" },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span>{item.label}</span>
                  <span className="text-slate-900 font-bold">{loading ? "–" : item.value} ветеранів</span>
                </div>
                <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${item.color} rounded-full transition-all duration-500`}
                    style={{ width: loading ? "0%" : `${stats.total_veterans_registered > 0 ? Math.min((item.value / totalNeeds) * 100, 100) : 0}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Останні відгуки на вакансії */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col">
          <div>
            <h3 className="font-bold text-slate-900 text-base flex items-center gap-2 mb-1">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              Останні відгуки ветеранів на вакансії
            </h3>
            <p className="text-xs text-slate-500 mb-4">Кандидати, що дали добровільну згоду на зв&apos;язок:</p>

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
                <div className="py-8 text-center text-slate-400">
                  Поки відгуків немає. Пройдіть шлях ветерана у розділі Вакансій!
                </div>
              )}
            </div>
          </div>

          <div className="pt-4 mt-auto border-t border-slate-100 text-[11px] text-slate-400 flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5" />
            Дані передаються суворо згідно з політикою згоди ветерана.
          </div>
        </div>
      </div>

      {/* Зауваження та відгуки */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <div>
            <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-amber-600" />
              Зауваження та відгуки (Сайт + Telegram-бот)
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">Всі звернення від ветеранів та партнерів для адміністратора платформи:</p>
          </div>
          <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-amber-100 text-amber-900">
            {loading ? "–" : feedbacks.length} повідомлень
          </span>
        </div>

        <div className="space-y-3">
          {!loading && feedbacks.length > 0 ? (
            feedbacks.map((item) => (
              <div key={item.id} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs space-y-1">
                <div className="flex items-center justify-between text-slate-500">
                  <span className="font-bold text-slate-800">
                    {item.sender_name || "Користувач"}{item.sender_contact ? ` (${item.sender_contact})` : ""}
                  </span>
                  <span className="text-[10px]">
                    {item.source} | {item.created_at}
                  </span>
                </div>
                <p className="text-slate-700 text-xs pt-0.5 leading-relaxed">{item.message}</p>
                <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-200 text-slate-600">
                  {item.category}
                </span>
              </div>
            ))
          ) : loading ? (
            <div className="text-center py-6 text-slate-400 text-xs">Завантаження...</div>
          ) : (
            <div className="text-center py-6 text-slate-400 text-xs">
              Зауважень ще не надходило. Скористайтеся кнопкою «Відгук» у шапці!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
