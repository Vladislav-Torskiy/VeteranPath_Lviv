"use client";

import { useState } from "react";
import { 
  Shield, Sparkles, Briefcase, Building2, HelpCircle, 
  Menu, X, User, LogIn, MessageSquarePlus 
} from "lucide-react";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  userPhone: string | null;
  userName: string | null;
  onOpenAuth: () => void;
  onOpenFeedback: () => void;
  onLogout: () => void;
}

export default function Navbar({
  activeTab,
  setActiveTab,
  userPhone,
  userName,
  onOpenAuth,
  onOpenFeedback,
  onLogout,
}: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleNav = (tab: string) => {
    setActiveTab(tab);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Логотип */}
        <div 
          onClick={() => handleNav("landing")}
          className="flex items-center gap-2 cursor-pointer select-none"
        >
          <div className="w-9 h-9 rounded-xl bg-slate-900 flex items-center justify-center text-white font-bold text-base shadow-sm">
            VP
          </div>
          <div>
            <span className="font-bold text-slate-900 tracking-tight text-base sm:text-lg">VeteranPath</span>
            <span className="ml-1 text-[10px] sm:text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-medium">Львівщина</span>
          </div>
        </div>

        {/* Навігація для десктопу */}
        <nav className="hidden lg:flex items-center gap-1">
          <button
            onClick={() => handleNav("roadmap")}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
              activeTab === "roadmap" ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <Shield className="w-4 h-4" />
            Дорожня карта
          </button>

          <button
            onClick={() => handleNav("resume")}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
              activeTab === "resume" ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <Sparkles className="w-4 h-4 text-emerald-400" />
            Мій досвід (Резюме)
          </button>

          <button
            onClick={() => handleNav("opportunities")}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
              activeTab === "opportunities" ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <Briefcase className="w-4 h-4" />
            Вакансії та Гранти
          </button>

          <button
            onClick={() => handleNav("chat")}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
              activeTab === "chat" ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <HelpCircle className="w-4 h-4" />
            Запитання (RAG)
          </button>
        </nav>

        {/* Дії справа (Авторизація + Відгук + Партнер) */}
        <div className="flex items-center gap-2">
          {/* Кнопка зауважень/фідбеку */}
          <button
            onClick={onOpenFeedback}
            title="Залишити зауваження або пропозицію"
            className="p-2 rounded-xl text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition hidden sm:flex items-center gap-1 text-xs font-medium"
          >
            <MessageSquarePlus className="w-4 h-4 text-amber-600" />
            <span>Відгук</span>
          </button>

          {/* Авторизація користувача */}
          {userPhone ? (
            <div className="flex items-center gap-1.5 bg-slate-100 rounded-xl px-2.5 py-1.5 text-xs text-slate-700">
              <User className="w-3.5 h-3.5 text-emerald-600" />
              <span className="font-semibold max-w-[90px] truncate">{userName || userPhone}</span>
              <button
                onClick={onLogout}
                className="text-[10px] text-slate-400 hover:text-red-600 ml-1 font-bold"
                title="Вийти"
              >
                ✕
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="px-3 py-1.5 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-semibold flex items-center gap-1.5 transition"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Увійти</span>
            </button>
          )}

          {/* Кабінет партнера */}
          <button
            onClick={() => handleNav("partner")}
            className={`hidden md:flex px-3 py-1.5 rounded-xl text-xs font-semibold transition items-center gap-1.5 border ${
              activeTab === "partner"
                ? "bg-emerald-600 text-white border-emerald-600 shadow-sm"
                : "border-slate-300 text-slate-700 hover:bg-slate-50"
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>Партнер/GovTech</span>
          </button>

          {/* Кнопка гамбургер-меню для мобільних */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Мобільне випадаюче меню */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-white border-b border-slate-200 px-4 pt-2 pb-4 space-y-1 animate-fade-in shadow-xl">
          <button
            onClick={() => handleNav("roadmap")}
            className={`w-full text-left px-3 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2.5 ${
              activeTab === "roadmap" ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
            }`}
          >
            <Shield className="w-4 h-4 text-emerald-500" />
            Дорожня карта дій
          </button>

          <button
            onClick={() => handleNav("resume")}
            className={`w-full text-left px-3 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2.5 ${
              activeTab === "resume" ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
            }`}
          >
            <Sparkles className="w-4 h-4 text-emerald-500" />
            Військовий перекладач резюме
          </button>

          <button
            onClick={() => handleNav("opportunities")}
            className={`w-full text-left px-3 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2.5 ${
              activeTab === "opportunities" ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
            }`}
          >
            <Briefcase className="w-4 h-4 text-blue-500" />
            Вакансії, курси та гранти
          </button>

          <button
            onClick={() => handleNav("chat")}
            className={`w-full text-left px-3 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2.5 ${
              activeTab === "chat" ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
            }`}
          >
            <HelpCircle className="w-4 h-4 text-purple-500" />
            Юридичний консультант (RAG)
          </button>

          <button
            onClick={() => handleNav("partner")}
            className={`w-full text-left px-3 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2.5 ${
              activeTab === "partner" ? "bg-emerald-700 text-white" : "text-slate-700 hover:bg-slate-100"
            }`}
          >
            <Building2 className="w-4 h-4 text-emerald-400" />
            Кабінет Партнера & GovTech
          </button>

          <button
            onClick={() => { onOpenFeedback(); setMobileMenuOpen(false); }}
            className="w-full text-left px-3 py-2.5 rounded-xl text-sm font-semibold text-amber-800 bg-amber-50 hover:bg-amber-100 flex items-center gap-2.5 mt-2"
          >
            <MessageSquarePlus className="w-4 h-4 text-amber-600" />
            Залишити зауваження / пропозицію
          </button>
        </div>
      )}
    </header>
  );
}
