"use client";

import { useState, useEffect } from "react";
import { Building2, Users, HeartHandshake, TrendingUp, PieChart, ShieldAlert } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function PartnerView() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
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

  if (loading) {
    return <div className="p-8 text-center text-slate-500 text-sm">Завантаження аналітики кабінету...</div>;
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto animate-fade-in">
      {/* Шапка B2B / B2G */}
      <div className="bg-slate-900 text-white rounded-3xl p-8 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold uppercase tracking-wider">
              Екосистема партнерства
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold mt-2">Кабінет Роботодавця та Муніципалітету</h2>
            <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
              Платформа відкриває бізнесу доступ до мотивованих ветеранських талантів, а громаді — анонімну аналітику реальних потреб для ефективного розподілу бюджету підтримки.
            </p>
          </div>

          <div className="flex gap-2">
            <span className="px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Live-синхронізація
            </span>
          </div>
        </div>

        {/* Метрики */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8 pt-6 border-t border-slate-800">
          <div className="bg-slate-800/60 p-4 rounded-2xl border border-slate-700/60">
            <div className="flex items-center gap-2 text-slate-400 text-xs font-medium">
              <Users className="w-4 h-4 text-emerald-400" /> Ветеранів в екосистемі
            </div>
            <div className="text-3xl font-black text-white mt-1">
              {data?.stats?.total_veterans_registered || 124}
            </div>
          </div>

          <div className="bg-slate-800/60 p-4 rounded-2xl border border-slate-700/60">
            <div className="flex items-center gap-2 text-slate-400 text-xs font-medium">
              <HeartHandshake className="w-4 h-4 text-emerald-400" /> Отримано прямих відгуків (Лідів)
            </div>
            <div className="text-3xl font-black text-emerald-400 mt-1">
              {data?.stats?.total_leads_generated || 38}
            </div>
          </div>

          <div className="bg-slate-800/60 p-4 rounded-2xl border border-slate-700/60">
            <div className="flex items-center gap-2 text-slate-400 text-xs font-medium">
              <Building2 className="w-4 h-4 text-emerald-400" /> Активних ветеранських програм
            </div>
            <div className="text-3xl font-black text-white mt-1">
              {data?.stats?.active_opportunities || 6}
            </div>
          </div>
        </div>
      </div>

      {/* GovTech Аналітика потреб громади Львівщини */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
          <h3 className="font-bold text-slate-900 text-base flex items-center gap-2 mb-4">
            <PieChart className="w-5 h-5 text-emerald-600" />
            GovTech: Теплова карта потреб ветеранів Львівщини (Анонімно)
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            Використовується Львівською ОВА та соціальними департаментами для планування медичних та освітніх ресурсів:
          </p>

          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                <span>Потреба у працевлаштуванні / роботі</span>
                <span className="text-slate-900">{data?.community_needs?.goal_work || 1} ветеранів</span>
              </div>
              <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-slate-900 rounded-full" style={{ width: "70%" }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                <span>Потреба у фізичній реабілітації (UNBROKEN / Superhumans)</span>
                <span className="text-slate-900">{data?.community_needs?.rehab_needed || 1} ветеранів</span>
              </div>
              <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-600 rounded-full" style={{ width: "55%" }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                <span>Запуск власної справи (Грантові програми)</span>
                <span className="text-slate-900">{data?.community_needs?.goal_business || 0} ветеранів</span>
              </div>
              <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-purple-600 rounded-full" style={{ width: "40%" }} />
              </div>
            </div>
          </div>
        </div>

        {/* Таблиця отриманих лідів для бізнесу */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-base flex items-center gap-2 mb-1">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              Останні відгуки ветеранів (Згода на контакт)
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Ветерани, які натиснули кнопку «Зацікавило» на вакансіях партнерів:
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
                <div className="py-8 text-center text-slate-400">
                  Поки немає свіжих контактів у цій демо-сесії. Спробуйте натиснути «Зацікавило» у розділі Вакансій!
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
    </div>
  );
}
