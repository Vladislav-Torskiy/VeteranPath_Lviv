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

  const navItems = [
    { id: "roadmap", icon: <Shield className="w-4 h-4" />, label: "Дорожня карта" },
    { id: "resume", icon: <Sparkles className="w-4 h-4 text-emerald-400" />, label: "Мій досвід" },
    { id: "opportunities", icon: <Briefcase className="w-4 h-4" />, label: "Вакансії та Гранти" },
    { id: "chat", icon: <HelpCircle className="w-4 h-4" />, label: "Запитання (RAG)" },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="h-14 flex items-center justify-between gap-2">

          {/* Логотип */}
          <button
            onClick={() => handleNav("landing")}
            className="flex items-center gap-2 shrink-0 cursor-pointer select-none"
          >
            <div className="w-8 h-8 rounded-xl bg-slate-900 flex items-center justify-center text-white font-bold text-sm shadow-sm">
              VP
            </div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-slate-900 text-sm sm:text-base leading-none">VeteranPath</span>
              <span className="hidden xs:inline text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-medium leading-none">
                Львівщина
              </span>
            </div>
          </button>

          {/* Навігація — тільки десктоп */}
          <nav className="hidden xl:flex items-center gap-0.5 mx-2">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleNav(item.id)}
                className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                  activeTab === item.id
                    ? "bg-slate-900 text-white"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                }`}
              >
                {item.icon}
                {item.label}
              </button>
            ))}
          </nav>

          {/* Права частина */}
          <div className="flex items-center gap-1.5 shrink-0">
            {/* Кнопка відгук */}
            <button
              onClick={onOpenFeedback}
              title="Залишити зауваження або пропозицію"
              className="hidden sm:flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition text-xs font-medium"
            >
              <MessageSquarePlus className="w-4 h-4 text-amber-600" />
              <span className="hidden md:inline">Відгук</span>
            </button>

            {/* Авторизація */}
            {userPhone ? (
              <div className="flex items-center gap-1 bg-slate-100 rounded-lg px-2 py-1.5 text-xs text-slate-700 max-w-[130px]">
                <User className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span className="font-semibold truncate">{userName || userPhone}</span>
                <button
                  onClick={onLogout}
                  className="text-[10px] text-slate-400 hover:text-red-600 font-bold ml-0.5 shrink-0"
                  title="Вийти"
                >
                  ✕
                </button>
              </div>
            ) : (
              <button
                onClick={onOpenAuth}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-semibold transition whitespace-nowrap"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Увійти</span>
              </button>
            )}

            {/* Кабінет партнера */}
            <button
              onClick={() => handleNav("partner")}
              className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition border whitespace-nowrap ${
                activeTab === "partner"
                  ? "bg-emerald-600 text-white border-emerald-600 shadow-sm"
                  : "border-slate-300 text-slate-700 hover:bg-slate-50"
              }`}
            >
              <Building2 className="w-3.5 h-3.5" />
              <span>Партнер</span>
            </button>

            {/* Гамбургер */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="xl:hidden p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Мобільне меню */}
      {mobileMenuOpen && (
        <div className="xl:hidden bg-white border-b border-slate-200 shadow-lg">
          <div className="max-w-7xl mx-auto px-3 py-3 space-y-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleNav(item.id)}
                className={`w-full text-left px-3 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2.5 ${
                  activeTab === item.id ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                {item.icon}
                {item.label}
              </button>
            ))}

            <button
              onClick={() => handleNav("partner")}
              className={`w-full text-left px-3 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2.5 ${
                activeTab === "partner" ? "bg-emerald-700 text-white" : "text-slate-700 hover:bg-slate-100"
              }`}
            >
              <Building2 className="w-4 h-4 text-emerald-500" />
              Кабінет Партнера & GovTech
            </button>

            <button
              onClick={() => { onOpenFeedback(); setMobileMenuOpen(false); }}
              className="w-full text-left px-3 py-2.5 rounded-xl text-sm font-semibold text-amber-800 bg-amber-50 hover:bg-amber-100 flex items-center gap-2.5"
            >
              <MessageSquarePlus className="w-4 h-4 text-amber-600" />
              Залишити зауваження / пропозицію
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
