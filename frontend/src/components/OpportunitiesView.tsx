"use client";

import { useState, useEffect } from "react";
import { Briefcase, Building, MapPin, CheckCircle, ExternalLink, Send, HeartHandshake } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function OpportunitiesView() {
  const [items, setItems] = useState<any[]>([]);
  const [filterType, setFilterType] = useState<string>("all");
  const [selectedOpp, setSelectedOpp] = useState<any>(null);
  const [contactChannel, setContactChannel] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  useEffect(() => {
    loadOpportunities();
  }, [filterType]);

  const loadOpportunities = async () => {
    try {
      const typeParam = filterType !== "all" ? `?type=${filterType}` : "";
      const data = await fetchApi(`/opportunities${typeParam}`);
      setItems(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleInterest = async () => {
    if (!contactChannel.trim() || !selectedOpp) return;
    setIsSubmitting(true);
    try {
      const token = localStorage.getItem("veteran_token") || "demo-token";
      await fetchApi("/opportunities/interest", {
        method: "POST",
        body: JSON.stringify({
          user_token: token,
          opportunity_id: selectedOpp.id,
          contact_channel: contactChannel,
        }),
      });
      setSuccessMsg("Ваш контакт успішно передано! Представник зв'яжеться з вами найближчим часом.");
      setTimeout(() => {
        setSuccessMsg("");
        setSelectedOpp(null);
        setContactChannel("");
      }, 3000);
    } catch (err) {
      console.error(err);
      alert("Помилка відправки запиту.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-fade-in">
      {/* Фільтри */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Програми та Вакансії Львівщини</h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Перевірені роботодавці з ветеранськими програмами, гранти та курси перекваліфікації.
          </p>
        </div>

        <div className="flex flex-wrap gap-1.5 p-1 bg-white border border-slate-200 rounded-xl">
          {[
            { id: "all", label: "Всі" },
            { id: "vacancy", label: "Вакансії" },
            { id: "course", label: "Курси" },
            { id: "grant", label: "Гранти" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilterType(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                filterType === tab.id ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Список карток */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map((opp) => (
          <div
            key={opp.id}
            className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between hover:border-slate-300 transition"
          >
            <div>
              <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
                <span className="font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                  {opp.type === "vacancy" ? "Вакансія" : opp.type === "course" ? "Навчання" : "Грант"}
                </span>
                <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {opp.location}</span>
              </div>

              <h3 className="text-lg font-bold text-slate-900">{opp.title}</h3>
              <p className="text-xs font-semibold text-slate-600 mt-0.5 flex items-center gap-1.5">
                <Building className="w-3.5 h-3.5 text-slate-400" />
                {opp.partner_name}
              </p>

              <p className="text-xs sm:text-sm text-slate-600 mt-3 leading-relaxed">{opp.description}</p>

              {opp.benefits && (
                <div className="mt-3 p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-700">
                  <strong className="text-slate-900">Ветеранський пакет:</strong> {opp.benefits}
                </div>
              )}
            </div>

            <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between">
              <span className="text-sm font-bold text-slate-900">{opp.salary_range || "За домовленістю"}</span>
              <button
                onClick={() => setSelectedOpp(opp)}
                className="px-4 py-2 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-semibold transition flex items-center gap-1.5"
              >
                <HeartHandshake className="w-4 h-4" />
                Зацікавило
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Модальне вікно "Зацікавило" */}
      {selectedOpp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 border border-slate-100">
            <h3 className="text-lg font-bold text-slate-900">Відгукнутися на пропозицію</h3>
            <p className="text-xs text-slate-500 mt-1 mb-4">
              <strong className="text-slate-800">{selectedOpp.title}</strong> — {selectedOpp.partner_name}
            </p>

            {successMsg ? (
              <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-200 text-sm text-emerald-900 font-medium text-center">
                ✅ {successMsg}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-blue-50 rounded-xl p-3 text-xs text-blue-800 space-y-1 border border-blue-100">
                  <p className="font-semibold">Як це працює:</p>
                  <p>1️⃣ Ви вказуєте свій контакт (Telegram або телефон)</p>
                  <p>2️⃣ Координатор програми бачить ваш контакт у своїй панелі</p>
                  <p>3️⃣ Вони зв&apos;язуються з вами для деталей та співбесіди</p>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                    Ваш контакт для зворотного зв&apos;язку:
                  </label>
                  <input
                    type="text"
                    value={contactChannel}
                    onChange={(e) => setContactChannel(e.target.value)}
                    placeholder="@telegram_нік або +380 97 000 00 00"
                    className="w-full p-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                  />
                  <p className="text-[11px] text-slate-400 mt-1.5">
                    🛡️ Контакт передається виключно цьому роботодавцю за вашою прямою згодою.
                  </p>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => { setSelectedOpp(null); setContactChannel(""); }}
                    className="flex-1 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-semibold text-xs hover:bg-slate-50 transition"
                  >
                    Скасувати
                  </button>
                  <button
                    onClick={handleInterest}
                    disabled={isSubmitting || !contactChannel.trim()}
                    className="flex-1 py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-semibold text-xs transition disabled:opacity-50 flex items-center justify-center gap-1.5"
                  >
                    {isSubmitting ? "Надсилання..." : "Підтвердити відгук"}
                    <Send className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
