"use client";

import { useState } from "react";
import { Sparkles, ArrowRight, Copy, Check, Briefcase, GraduationCap, Award } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function ResumeTranslator() {
  const [militaryText, setMilitaryText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [translatedData, setTranslatedData] = useState<any>(null);
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  const handleTranslate = async () => {
    if (!militaryText.trim()) return;
    setIsLoading(true);
    try {
      const res = await fetchApi("/experience/translate", {
        method: "POST",
        body: JSON.stringify({ experience_text: militaryText }),
      });
      setTranslatedData(res);
    } catch (err) {
      console.error(err);
      alert("Не вдалося перекласти досвід.");
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(index);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fade-in">
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="w-5 h-5 text-emerald-600" />
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900">
            «Військовий перекладач»: з армії в цивільне резюме
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-500 mb-5">
          Введіть своїми словами, чим ви займалися на службі: командування, водіння, логістика, зв'язок або ремонт. ШІ перекладе це на мову бізнес-компетенцій.
        </p>

        <textarea
          rows={4}
          value={militaryText}
          onChange={(e) => setMilitaryText(e.target.value)}
          placeholder="Наприклад: Командир відділення, відповідав за 9 бійців, боєкомплект, підвезення провізії, заповнення журналів, обслуговування пікапів та радіостанцій Motorola..."
          className="w-full p-4 rounded-xl border border-slate-300 focus:ring-2 focus:ring-emerald-500 outline-none text-sm leading-relaxed"
        />

        <div className="mt-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <button
            type="button"
            onClick={() => setMilitaryText("Командував відділенням, відповідав за особовий склад з 10 людей, розподіл боєприпасів і пального, контроль технічного стану двох автомобілів, швидке прийняття рішень під час критичних ситуацій.")}
            className="text-xs text-emerald-700 hover:underline font-medium"
          >
            💡 Вставити приклад «Командир відділення / Логіст»
          </button>

          <button
            onClick={handleTranslate}
            disabled={isLoading || !militaryText.trim()}
            className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm flex items-center justify-center gap-2 transition disabled:opacity-50"
          >
            {isLoading ? "Переклад..." : "Трансформувати в навички"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {translatedData && (
        <div className="space-y-6">
          {/* Сформовані формулювання для резюме */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2 mb-3">
              <Award className="w-5 h-5 text-emerald-600" />
              Готові формулювання для вашого резюме (Bullet points)
            </h3>
            <div className="space-y-3">
              {translatedData.resume_bullet_points.map((point: string, idx: number) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 flex items-start justify-between gap-3 group"
                >
                  <p className="text-sm text-slate-800 leading-relaxed">{point}</p>
                  <button
                    onClick={() => copyToClipboard(point, idx)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-700 hover:bg-white transition shrink-0"
                    title="Скопіювати формулювання"
                  >
                    {copiedIdx === idx ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Навички */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2 mb-3">
                <Briefcase className="w-5 h-5 text-blue-600" />
                Виділені цивільні навички (Hard & Soft Skills)
              </h3>
              <ul className="space-y-2">
                {translatedData.civilian_skills.map((skill: string, idx: number) => (
                  <li key={idx} className="flex items-center gap-2 text-sm text-slate-700">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
                    {skill}
                  </li>
                ))}
              </ul>
            </div>

            {/* Професії та курси для закриття прогалин */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2 mb-3">
                <GraduationCap className="w-5 h-5 text-purple-600" />
                Професії та рекомендовані курси
              </h3>
              <div className="space-y-3">
                {translatedData.skill_gaps_and_courses.map((item: any, idx: number) => (
                  <div key={idx} className="p-3 bg-purple-50/60 rounded-xl border border-purple-100 text-xs sm:text-sm">
                    <strong className="text-purple-950 font-bold block">{item.role}</strong>
                    <p className="text-slate-600 mt-0.5"><span className="text-purple-800 font-medium">Чого бракує:</span> {item.gap}</p>
                    <p className="text-slate-600 mt-0.5"><span className="text-purple-800 font-medium">Курс:</span> {item.course}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
