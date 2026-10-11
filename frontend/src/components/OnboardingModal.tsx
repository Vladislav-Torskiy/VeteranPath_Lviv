"use client";

import { useState } from "react";
import { Sparkles, ArrowRight, ShieldCheck, FileCheck, CheckCircle2 } from "lucide-react";
import { fetchApi } from "@/lib/api";

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCompleted: (userToken: string) => void;
}

export default function OnboardingModal({ isOpen, onClose, onCompleted }: OnboardingModalProps) {
  const [tab, setTab] = useState<"freetext" | "form">("freetext");
  const [freeText, setFreeText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [parsedPreview, setParsedPreview] = useState<any>(null);

  // Стан для форми
  const [formData, setFormData] = useState({
    status: "ubd",
    region: "Львівська область",
    city: "Львів",
    health_status: "none",
    primary_goal: "work",
    education: "Вища / середня спеціальна",
    demobilized_date: "Останній місяць"
  });

  if (!isOpen) return null;

  const handleFreeTextParse = async () => {
    if (!freeText.trim()) return;
    setIsLoading(true);
    try {
      const res = await fetchApi("/onboarding/parse-text", {
        method: "POST",
        body: JSON.stringify({ text: freeText }),
      });
      setParsedPreview(res);
      setFormData(res.parsed_profile);
    } catch (err) {
      console.error(err);
      alert("Не вдалося обробити текст. Спробуйте швидку форму.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveAndStart = async () => {
    setIsLoading(true);
    try {
      const storedToken = localStorage.getItem("veteran_token") || "";
      const res = await fetchApi("/onboarding/save-profile", {
        method: "POST",
        body: JSON.stringify({
          ...formData,
          user_token: storedToken || undefined,
        }),
      });

      localStorage.setItem("veteran_token", res.user_token);
      onCompleted(res.user_token);
      onClose();
    } catch (err) {
      console.error(err);
      alert("Помилка збереження профілю.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6 sm:p-8 max-h-[90vh] overflow-y-auto border border-slate-100">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900">Скласти мій персональний план</h2>
            <p className="text-xs sm:text-sm text-slate-500 mt-1 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              100% анонімно. Жодних паспортів, телефонів чи пошти при старті.
            </p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 font-bold p-1">
            ✕
          </button>
        </div>

        {/* Перемикач режиму онбордингу */}
        <div className="flex p-1 bg-slate-100 rounded-xl my-5">
          <button
            onClick={() => setTab("freetext")}
            className={`flex-1 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              tab === "freetext" ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Sparkles className="w-4 h-4 text-emerald-600" />
            Вільним текстом (ШІ аналіз)
          </button>
          <button
            onClick={() => setTab("form")}
            className={`flex-1 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              tab === "form" ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <FileCheck className="w-4 h-4 text-blue-600" />
            Швидка форма (вибір полів)
          </button>
        </div>

        {tab === "freetext" ? (
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Розкажіть про себе своїми словами:
            </label>
            <textarea
              rows={4}
              value={freeText}
              onChange={(e) => setFreeText(e.target.value)}
              placeholder="Наприклад: Демобілізувався місяць тому, 80-та десантно-штурмова бригада у Львові. Маю поранення коліна, потребую курсу реабілітації. Хочу знайти роботу у сфері логістики або відкрити власну кав'ярню..."
              className="w-full p-3.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm outline-none transition"
            />
            
            <div className="mt-3 flex items-center justify-between">
              <button
                type="button"
                onClick={() => setFreeText("Служив командиром відділення у 80-й бригаді ДШВ, Львів, поранення коліна, потребую реабілітації, хочу знайти роботу в логістиці або отримати грант на кав'ярню")}
                className="text-xs text-emerald-700 hover:underline font-medium"
              >
                💡 Вставити демо-сценарій «Ветеран Андрій»
              </button>
              
              <button
                onClick={handleFreeTextParse}
                disabled={isLoading || !freeText.trim()}
                className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-medium text-sm flex items-center gap-2 disabled:opacity-50 transition"
              >
                {isLoading ? "Аналіз ШІ..." : "Розпізнати параметри"}
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>

            {parsedPreview && (
              <div className="mt-5 p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                <div className="flex items-start gap-2.5">
                  <CheckCircle2 className="w-5 h-5 text-emerald-700 mt-0.5 shrink-0" />
                  <div>
                    <h4 className="text-sm font-semibold text-emerald-950">ШІ сформував ваш профіль:</h4>
                    <p className="text-xs text-emerald-900 mt-1 leading-relaxed">{parsedPreview.summary_message}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 mt-3 pt-3 border-t border-emerald-200/60 text-xs">
                  <div><span className="text-slate-500">Статус:</span> <strong className="text-slate-800">{formData.status}</strong></div>
                  <div><span className="text-slate-500">Локація:</span> <strong className="text-slate-800">{formData.city}</strong></div>
                  <div><span className="text-slate-500">Здоров'я:</span> <strong className="text-slate-800">{formData.health_status}</strong></div>
                  <div><span className="text-slate-500">Пріоритет:</span> <strong className="text-slate-800">{formData.primary_goal}</strong></div>
                </div>

                <button
                  onClick={handleSaveAndStart}
                  disabled={isLoading}
                  className="w-full mt-4 py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-semibold text-sm transition shadow-sm"
                >
                  Підтвердити та відкрити дорожню карту
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Ваш статус</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                >
                  <option value="ubd">Учасник бойових дій (УБД)</option>
                  <option value="active_duty">Діючий військовослужбовець</option>
                  <option value="disability">Особа з інвалідністю внаслідок війни</option>
                  <option value="family_member">Член родини захисника</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Громада / Місто</label>
                <select
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                >
                  <option value="Львів">м. Львів</option>
                  <option value="Дрогобич">м. Дрогобич</option>
                  <option value="Стрий">м. Стрий</option>
                  <option value="Червоноград">м. Червоноград</option>
                  <option value="Інша громада області">Інша громада Львівщини</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Потреба у реабілітації</label>
                <select
                  value={formData.health_status}
                  onChange={(e) => setFormData({ ...formData, health_status: e.target.value })}
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                >
                  <option value="none">Не потребую (стан задовільний)</option>
                  <option value="rehab_needed">Потребую фізичної реабілітації (UNBROKEN)</option>
                  <option value="prosthetics_needed">Потребую протезування (Superhumans)</option>
                  <option value="psychological">Потребую психологічної підтримки</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Головна ціль наразі</label>
                <select
                  value={formData.primary_goal}
                  onChange={(e) => setFormData({ ...formData, primary_goal: e.target.value })}
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                >
                  <option value="work">Знайти гідну роботу / кар'єра</option>
                  <option value="business">Запустити власну справу (грант)</option>
                  <option value="education">Пройти курси / перекваліфікація</option>
                  <option value="health">Зосередитися на лікуванні</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleSaveAndStart}
              disabled={isLoading}
              className="w-full mt-4 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm transition shadow-md flex items-center justify-center gap-2"
            >
              {isLoading ? "Збереження..." : "Скласти мій персональний план"}
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
