"use client";

import { useState } from "react";
import { CheckCircle2, Circle, Clock, MapPin, FileText, ExternalLink, ChevronDown, ChevronUp, AlertCircle } from "lucide-react";
import { fetchApi } from "@/lib/api";

interface Step {
  id: string;
  title: string;
  stage: string;
  stage_title: string;
  priority: number;
  category: string;
  short_description: string;
  required_documents: string[];
  where_to_go: string;
  estimated_time: string;
  official_source: string;
  last_verified_at: string;
  is_completed: boolean;
}

interface RoadmapViewProps {
  roadmapData: {
    user_token: string;
    total_steps: number;
    completed_steps: number;
    progress_percentage: number;
    priority_steps: Step[];
    stages: Record<string, { title: string; steps: Step[] }>;
  };
  onRefresh: () => void;
}

export default function RoadmapView({ roadmapData, onRefresh }: RoadmapViewProps) {
  const [expandedStep, setExpandedStep] = useState<string | null>(null);
  const [loadingStepId, setLoadingStepId] = useState<string | null>(null);

  const toggleStep = async (stepId: string, currentStatus: boolean) => {
    setLoadingStepId(stepId);
    try {
      await fetchApi("/roadmap/toggle-step", {
        method: "POST",
        body: JSON.stringify({
          user_token: roadmapData.user_token,
          step_id: stepId,
          is_completed: !currentStatus,
        }),
      });
      onRefresh();
    } catch (err) {
      console.error(err);
      alert("Не вдалося оновити статус кроку.");
    } finally {
      setLoadingStepId(null);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Прогрес-бар та індикатор */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <span className="text-xs uppercase font-bold text-emerald-700 tracking-wider">Ваш прогрес інтеграції</span>
            <h2 className="text-2xl font-bold text-slate-900 mt-0.5">
              Виконано {roadmapData.completed_steps} із {roadmapData.total_steps} кроків
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-3xl font-extrabold text-slate-900">{roadmapData.progress_percentage}%</span>
            <span className="text-xs text-slate-500 font-medium max-w-[80px] leading-tight">готовності плану</span>
          </div>
        </div>

        {/* Смужка прогресу */}
        <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-emerald-600 rounded-full transition-all duration-500"
            style={{ width: `${roadmapData.progress_percentage}%` }}
          />
        </div>
      </div>

      {/* Блок «Зараз найважливіше» (Priority steps) */}
      {roadmapData.priority_steps.length > 0 && (
        <div className="bg-amber-50/70 border border-amber-200 rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-5 h-5 text-amber-700" />
            <h3 className="text-base font-bold text-amber-950">Зараз найважливіше (Першочергові кроки)</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {roadmapData.priority_steps.map((step) => (
              <div
                key={step.id}
                className="bg-white rounded-xl p-4 border border-amber-200/80 shadow-sm flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
                    <span className="font-semibold text-emerald-700">{step.category.toUpperCase()}</span>
                    <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {step.estimated_time}</span>
                  </div>
                  <h4 className="font-bold text-sm text-slate-900 line-clamp-2">{step.title}</h4>
                  <p className="text-xs text-slate-600 mt-1 line-clamp-2">{step.short_description}</p>
                </div>

                <button
                  onClick={() => toggleStep(step.id, step.is_completed)}
                  disabled={loadingStepId === step.id}
                  className="mt-4 w-full py-1.5 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 bg-slate-900 hover:bg-slate-800 text-white transition"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Позначити виконаним
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Етапи дорожньої карти */}
      <div className="space-y-6">
        {Object.entries(roadmapData.stages).map(([stageKey, stageData]) => (
          <div key={stageKey} className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <h3 className="text-lg font-bold text-slate-900 pb-3 border-b border-slate-100 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
              {stageData.title}
            </h3>

            <div className="divide-y divide-slate-100 mt-2">
              {stageData.steps.map((step) => {
                const isExpanded = expandedStep === step.id;
                return (
                  <div key={step.id} className="py-4 first:pt-2 last:pb-1">
                    <div className="flex items-start justify-between gap-3">
                      <button
                        onClick={() => toggleStep(step.id, step.is_completed)}
                        disabled={loadingStepId === step.id}
                        className="mt-0.5 text-slate-400 hover:text-emerald-600 transition shrink-0"
                      >
                        {step.is_completed ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-600 fill-emerald-50" />
                        ) : (
                          <Circle className="w-5 h-5" />
                        )}
                      </button>

                      <div className="flex-1 cursor-pointer" onClick={() => setExpandedStep(isExpanded ? null : step.id)}>
                        <div className="flex items-center gap-2 flex-wrap">
                          <h4 className={`text-sm sm:text-base font-semibold ${step.is_completed ? "line-through text-slate-400" : "text-slate-900"}`}>
                            {step.title}
                          </h4>
                          {step.priority === 1 && (
                            <span className="text-[10px] font-bold px-1.5 py-0.5 bg-red-100 text-red-700 rounded">Пріоритет</span>
                          )}
                        </div>
                        <p className="text-xs sm:text-sm text-slate-600 mt-1">{step.short_description}</p>
                      </div>

                      <button
                        onClick={() => setExpandedStep(isExpanded ? null : step.id)}
                        className="text-slate-400 hover:text-slate-600 p-1"
                      >
                        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </button>
                    </div>

                    {/* Розгорнутий детальний блок */}
                    {isExpanded && (
                      <div className="mt-4 ml-8 p-4 bg-slate-50 rounded-xl border border-slate-200/60 text-xs sm:text-sm space-y-3 animate-fade-in">
                        <div>
                          <span className="font-semibold text-slate-700 flex items-center gap-1.5 mb-1.5">
                            <FileText className="w-4 h-4 text-slate-500" />
                            Необхідні документи:
                          </span>
                          <ul className="list-disc list-inside space-y-1 text-slate-600 pl-1">
                            {step.required_documents.map((doc, idx) => (
                              <li key={idx}>{doc}</li>
                            ))}
                          </ul>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-slate-200">
                          <div>
                            <span className="font-semibold text-slate-700 flex items-center gap-1">
                              <MapPin className="w-3.5 h-3.5 text-slate-500" /> Куди звертатися:
                            </span>
                            <p className="text-slate-600 mt-0.5">{step.where_to_go}</p>
                          </div>
                          <div>
                            <span className="font-semibold text-slate-700 flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5 text-slate-500" /> Орієнтовний термін:
                            </span>
                            <p className="text-slate-600 mt-0.5">{step.estimated_time}</p>
                          </div>
                        </div>

                        <div className="pt-2 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
                          <span>Джерело: <strong className="text-slate-700">{step.official_source}</strong></span>
                          <span>Перевірено: {step.last_verified_at}</span>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
