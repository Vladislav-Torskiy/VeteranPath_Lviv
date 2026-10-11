"use client";

import { Shield, Sparkles, MapPin, Briefcase, Building2, HelpCircle } from "lucide-react";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export default function Navbar({ activeTab, setActiveTab }: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div 
          onClick={() => setActiveTab("landing")}
          className="flex items-center gap-2 cursor-pointer select-none"
        >
          <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-white font-bold text-lg shadow-sm">
            VP
          </div>
          <div>
            <span className="font-bold text-slate-900 tracking-tight text-lg">VeteranPath</span>
            <span className="ml-1 text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-medium">Львівщина</span>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-1">
          <button
            onClick={() => setActiveTab("roadmap")}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
              activeTab === "roadmap" ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <Shield className="w-4 h-4" />
            Дорожня карта
          </button>

          <button
            onClick={() => setActiveTab("resume")}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
              activeTab === "resume" ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <Sparkles className="w-4 h-4 text-emerald-400" />
            Мій досвід (AI Резюме)
          </button>

          <button
            onClick={() => setActiveTab("opportunities")}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
              activeTab === "opportunities" ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <Briefcase className="w-4 h-4" />
            Вакансії та Гранти
          </button>

          <button
            onClick={() => setActiveTab("chat")}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
              activeTab === "chat" ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <HelpCircle className="w-4 h-4" />
            Запитання (RAG)
          </button>
        </nav>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab("partner")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all flex items-center gap-1.5 border ${
              activeTab === "partner"
                ? "bg-emerald-600 text-white border-emerald-600 shadow-sm"
                : "border-slate-300 text-slate-700 hover:bg-slate-50"
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            Кабінет партнера / GovTech
          </button>
        </div>
      </div>
    </header>
  );
}
