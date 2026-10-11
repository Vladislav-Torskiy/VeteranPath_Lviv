"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import OnboardingModal from "@/components/OnboardingModal";
import RoadmapView from "@/components/RoadmapView";
import ResumeTranslator from "@/components/ResumeTranslator";
import OpportunitiesView from "@/components/OpportunitiesView";
import ChatView from "@/components/ChatView";
import PartnerView from "@/components/PartnerView";
import { fetchApi } from "@/lib/api";
import { Shield, Sparkles, ArrowRight, HeartHandshake, CheckCircle2, Building2 } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>("landing");
  const [isOnboardingOpen, setIsOnboardingOpen] = useState(false);
  const [userToken, setUserToken] = useState<string>("");
  const [roadmapData, setRoadmapData] = useState<any>(null);
  const [isLoadingRoadmap, setIsLoadingRoadmap] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("veteran_token");
    if (token) {
      setUserToken(token);
      loadRoadmap(token);
    }
  }, []);

  const loadRoadmap = async (token: string) => {
    setIsLoadingRoadmap(true);
    try {
      const data = await fetchApi(`/roadmap?user_token=${token}`);
      setRoadmapData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoadingRoadmap(false);
    }
  };

  const handleOnboardingCompleted = (token: string) => {
    setUserToken(token);
    loadRoadmap(token);
    setActiveTab("roadmap");
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Вкладка 1: ЛЕНДІНГ */}
        {activeTab === "landing" && (
          <div className="space-y-12 animate-fade-in py-6">
            {/* Hero блок */}
            <div className="text-center max-w-3xl mx-auto space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                Екосистема повернення до цивільного життя на Львівщині
              </div>

              <h1 className="text-4xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
                Від демобілізації до впевненого цивільного життя.
              </h1>

              <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
                Персональний покроковий план: оформлення статусів, виплати, відновлення у центрах UNBROKEN та Superhumans, переклад військового досвіду для резюме та гранти на власну справу.
              </p>

              <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-4">
                <button
                  onClick={() => setIsOnboardingOpen(true)}
                  className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-base shadow-lg hover:shadow-xl transition flex items-center justify-center gap-2.5 group"
                >
                  Скласти мій персональний план
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition" />
                </button>

                <button
                  onClick={() => setActiveTab("partner")}
                  className="w-full sm:w-auto px-6 py-4 rounded-2xl bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 font-semibold text-sm transition flex items-center justify-center gap-2"
                >
                  <Building2 className="w-4 h-4 text-emerald-600" />
                  Для партнерів та громад
                </button>
              </div>

              {/* Захист даних */}
              <div className="pt-4 flex items-center justify-center gap-6 text-xs text-slate-500 font-medium">
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Без реєстрації та номерів телефонів
                </span>
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Перевірені юридичні джерела
                </span>
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Безкоштовно для ветеранів
                </span>
              </div>
            </div>

            {/* Три ключові стовпи платформи */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-900 font-bold">
                  01
                </div>
                <h3 className="text-lg font-bold text-slate-900">Покрокова карта дій</h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Не потрібно блукати кабінетами. Чіткий список: що оформити в 1-й тиждень, 1-й місяць і за 3 місяці з точними адресами ЦНАП та документами.
                </p>
              </div>

              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-800 font-bold">
                  02
                </div>
                <h3 className="text-lg font-bold text-slate-900">Військовий перекладач резюме</h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  ШІ трансформує службу (командування, логістику, керування технікою) на мову цивільних роботодавців, показуючи конкретні переваги перед іншими кандидатами.
                </p>
              </div>

              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center text-blue-800 font-bold">
                  03
                </div>
                <h3 className="text-lg font-bold text-slate-900">Екосистема Львівщини</h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Пряма інтеграція з Superhumans, центром UNBROKEN, міськими виплатами Львова та грантами «єРобота» до 1 млн грн на відкриття власної справи.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Вкладка 2: ДОРОЖНЯ КАРТА */}
        {activeTab === "roadmap" && (
          <div>
            {roadmapData ? (
              <RoadmapView
                roadmapData={roadmapData}
                onRefresh={() => loadRoadmap(userToken)}
              />
            ) : (
              <div className="text-center py-16 space-y-4 bg-white rounded-3xl p-8 border border-slate-200">
                <Shield className="w-12 h-12 text-slate-400 mx-auto" />
                <h3 className="text-xl font-bold text-slate-900">Ваш план ще не складено</h3>
                <p className="text-sm text-slate-500 max-w-md mx-auto">
                  Дайте відповіді на кілька простих запитань або опишіть ситуацію вільним текстом, щоб система згенерувала вашу персональну карту.
                </p>
                <button
                  onClick={() => setIsOnboardingOpen(true)}
                  className="px-6 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm transition"
                >
                  Скласти мій план зараз
                </button>
              </div>
            )}
          </div>
        )}

        {/* Вкладка 3: МІЙ ДОСВІД (РЕЗЮМЕ) */}
        {activeTab === "resume" && <ResumeTranslator />}

        {/* Вкладка 4: ВАКАНСІЇ ТА МОЖЛИВОСТІ */}
        {activeTab === "opportunities" && <OpportunitiesView />}

        {/* Вкладка 5: ЧАТ З ДЖЕРЕЛАМИ */}
        {activeTab === "chat" && <ChatView />}

        {/* Вкладка 6: КАБІНЕТ ПАРТНЕРА */}
        {activeTab === "partner" && <PartnerView />}
      </main>

      {/* Футер */}
      <footer className="border-t border-slate-200 bg-white py-6 mt-12 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2025-2026 VeteranPath Lviv. Довідковий сервіс для підтримки захисників та їхніх родин.</p>
          <p className="text-slate-400">Остаточні юридичні рішення ухвалюються уповноваженими органами державної влади.</p>
        </div>
      </footer>

      {/* Модальне вікно онбордингу */}
      <OnboardingModal
        isOpen={isOnboardingOpen}
        onClose={() => setIsOnboardingOpen(false)}
        onCompleted={handleOnboardingCompleted}
      />
    </div>
  );
}
