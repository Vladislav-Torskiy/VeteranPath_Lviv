"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import OnboardingModal from "@/components/OnboardingModal";
import AuthModal from "@/components/AuthModal";
import FeedbackModal from "@/components/FeedbackModal";
import RoadmapView from "@/components/RoadmapView";
import ResumeTranslator from "@/components/ResumeTranslator";
import OpportunitiesView from "@/components/OpportunitiesView";
import ChatView from "@/components/ChatView";
import PartnerView from "@/components/PartnerView";
import { fetchApi } from "@/lib/api";
import { 
  Shield, Sparkles, ArrowRight, CheckCircle2, 
  Building2, Smartphone, Award, FileText 
} from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>("landing");
  const [isOnboardingOpen, setIsOnboardingOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);
  
  const [userToken, setUserToken] = useState<string>("");
  const [userPhone, setUserPhone] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);

  const [roadmapData, setRoadmapData] = useState<any>(null);
  const [isLoadingRoadmap, setIsLoadingRoadmap] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("veteran_token");
    const phone = localStorage.getItem("veteran_phone");
    const name = localStorage.getItem("veteran_name");
    
    if (phone) setUserPhone(phone);
    if (name) setUserName(name);

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

  const handleAuthSuccess = (data: { user_token: string; phone: string; full_name?: string }) => {
    setUserToken(data.user_token);
    setUserPhone(data.phone);
    if (data.full_name) setUserName(data.full_name);
    loadRoadmap(data.user_token);
  };

  const handleLogout = () => {
    localStorage.removeItem("veteran_phone");
    localStorage.removeItem("veteran_name");
    setUserPhone(null);
    setUserName(null);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        userPhone={userPhone}
        userName={userName}
        onOpenAuth={() => setIsAuthOpen(true)}
        onOpenFeedback={() => setIsFeedbackOpen(true)}
        onLogout={handleLogout}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-3 sm:px-6 lg:px-8 py-5 sm:py-8">
        {/* Вкладка 1: ЛЕНДІНГ */}
        {activeTab === "landing" && (
          <div className="space-y-10 sm:space-y-14 animate-fade-in py-2 sm:py-6">
            {/* Hero блок */}
            <div className="text-center max-w-3xl mx-auto space-y-4 sm:space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                Екосистема повернення до цивільного життя на Львівщині
              </div>

              <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
                Від демобілізації до впевненого цивільного життя.
              </h1>

              <p className="text-sm sm:text-lg text-slate-600 leading-relaxed px-2">
                Персональний план дій: оформлення статусів, виплати, відновлення у центрах UNBROKEN та Superhumans, адаптація досвіду для резюме та гранти на власну справу.
              </p>

              {/* Дії на лендінгу */}
              <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 px-2">
                <button
                  onClick={() => setIsOnboardingOpen(true)}
                  className="w-full sm:w-auto px-7 py-3.5 sm:py-4 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm sm:text-base shadow-lg hover:shadow-xl transition flex items-center justify-center gap-2.5 group"
                >
                  Скласти мій персональний план
                  <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5 group-hover:translate-x-1 transition" />
                </button>

                {!userPhone && (
                  <button
                    onClick={() => setIsAuthOpen(true)}
                    className="w-full sm:w-auto px-6 py-3.5 sm:py-4 rounded-2xl bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 font-semibold text-xs sm:text-sm transition flex items-center justify-center gap-2"
                  >
                    <Smartphone className="w-4 h-4 text-emerald-600" />
                    Увійти за номером телефону
                  </button>
                )}
              </div>

              {/* Безпека і довіра */}
              <div className="pt-3 flex flex-wrap items-center justify-center gap-3 sm:gap-6 text-[11px] sm:text-xs text-slate-500 font-medium">
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Доступно зі смартфона та ПК
                </span>
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Перевірені юридичні джерела
                </span>
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Безкоштовно для захисників
                </span>
              </div>
            </div>

            {/* Три ключові стовпи платформи */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 pt-4">
              <div className="bg-white p-5 sm:p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2.5">
                <div className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center text-slate-900 font-bold text-sm">
                  01
                </div>
                <h3 className="text-base sm:text-lg font-bold text-slate-900">Покрокова карта дій</h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Чіткий список: що оформити в 1-й тиждень, 1-й місяць і за 3 місяці з точними адресами ЦНАП та переліком необхідних документів.
                </p>
              </div>

              <div className="bg-white p-5 sm:p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2.5">
                <div className="w-9 h-9 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-800 font-bold text-sm">
                  02
                </div>
                <h3 className="text-base sm:text-lg font-bold text-slate-900">Військовий перекладач резюме</h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  ШІ трансформує службу (командування, логістику, керування технікою) на мову бізнес-навичок та готує формулювання для резюме.
                </p>
              </div>

              <div className="bg-white p-5 sm:p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2.5">
                <div className="w-9 h-9 rounded-xl bg-blue-100 flex items-center justify-center text-blue-800 font-bold text-sm">
                  03
                </div>
                <h3 className="text-base sm:text-lg font-bold text-slate-900">Екосистема Львівщини</h3>
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
              <div className="text-center py-12 sm:py-16 space-y-4 bg-white rounded-3xl p-6 sm:p-8 border border-slate-200">
                <Shield className="w-12 h-12 text-slate-400 mx-auto" />
                <h3 className="text-lg sm:text-xl font-bold text-slate-900">Ваш план ще не складено</h3>
                <p className="text-xs sm:text-sm text-slate-500 max-w-md mx-auto">
                  Дайте відповіді на кілька простих запитань або опишіть ситуацію вільним текстом, щоб система згенерувала вашу персональну карту.
                </p>
                <div className="flex flex-col sm:flex-row gap-2 justify-center pt-2">
                  <button
                    onClick={() => setIsOnboardingOpen(true)}
                    className="px-6 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs sm:text-sm transition"
                  >
                    Скласти мій план зараз
                  </button>
                  <button
                    onClick={() => setIsAuthOpen(true)}
                    className="px-6 py-3 rounded-xl border border-slate-300 hover:bg-slate-50 text-slate-700 font-semibold text-xs sm:text-sm transition"
                  >
                    Увійти за телефоном
                  </button>
                </div>
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
      <footer className="border-t border-slate-200 bg-white py-6 mt-8 sm:mt-12 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
          <p>© 2025-2026 VeteranPath Lviv. Довідковий сервіс для підтримки захисників та їхніх родин.</p>
          <div className="flex items-center gap-4 text-slate-600">
            <button onClick={() => setIsFeedbackOpen(true)} className="hover:text-emerald-700 underline">
              Повідомити про проблему
            </button>
            <span className="text-slate-300">|</span>
            <span>Львів, Україна</span>
          </div>
        </div>
      </footer>

      {/* Модальні вікна */}
      <OnboardingModal
        isOpen={isOnboardingOpen}
        onClose={() => setIsOnboardingOpen(false)}
        onCompleted={handleOnboardingCompleted}
      />

      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onSuccess={handleAuthSuccess}
      />

      <FeedbackModal
        isOpen={isFeedbackOpen}
        onClose={() => setIsFeedbackOpen(false)}
      />
    </div>
  );
}
