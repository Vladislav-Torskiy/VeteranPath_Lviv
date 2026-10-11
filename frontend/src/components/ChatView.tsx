"use client";

import { useState } from "react";
import { HelpCircle, Send, BookOpen, PhoneCall, ShieldCheck } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function ChatView() {
  const [messages, setMessages] = useState<any[]>([
    {
      sender: "bot",
      text: "Вітаю! Я юридичний помічник VeteranPath. Відповідаю виключно за перевіреними законами, постановами та місцевими програмами Львівщини. Запитайте про УБД, виплати за поранення, центри UNBROKEN або гранти єРобота.",
      sources: ["Законодавство про статус ветеранів війни", "Постанови КМУ"],
      hotlines: ["1545 (Ветеранська урядова лінія)"],
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (questionText?: string) => {
    const q = questionText || input;
    if (!q.trim()) return;

    const newMsgs = [...messages, { sender: "user", text: q }];
    setMessages(newMsgs);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetchApi("/chat/ask", {
        method: "POST",
        body: JSON.stringify({ question: q }),
      });

      setMessages([
        ...newMsgs,
        {
          sender: "bot",
          text: res.answer,
          sources: res.sources,
          hotlines: res.recommended_hotlines,
        },
      ]);
    } catch (err) {
      console.error(err);
      setMessages([
        ...newMsgs,
        {
          sender: "bot",
          text: "Вибачте, виникла помилка зв'язку. Будь ласка, зверніться на гарячу лінію 1545.",
          sources: [],
          hotlines: ["1545"],
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-4 animate-fade-in">
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col h-[600px]">
        {/* Заголовок */}
        <div className="pb-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-800">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Перевірений юридичний консультант (RAG)</h3>
              <p className="text-[11px] text-slate-500">Без вигадок: обов'язкові посилання на закони та ЦНАП Львова</p>
            </div>
          </div>
        </div>

        {/* Стрічка повідомлень */}
        <div className="flex-1 overflow-y-auto py-4 space-y-4 pr-1">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${m.sender === "user" ? "items-end" : "items-start"}`}
            >
              <div
                className={`max-w-[85%] p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                  m.sender === "user"
                    ? "bg-slate-900 text-white rounded-tr-none"
                    : "bg-slate-50 border border-slate-200/80 text-slate-800 rounded-tl-none"
                }`}
              >
                <p>{m.text}</p>

                {m.sources && m.sources.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-slate-200/60 text-[11px] text-slate-500 space-y-1">
                    <div className="font-semibold text-slate-700 flex items-center gap-1">
                      <BookOpen className="w-3 h-3 text-emerald-600" /> Джерело перевірки:
                    </div>
                    {m.sources.map((s: string, sIdx: number) => (
                      <div key={sIdx} className="text-slate-600">🏛️ {s}</div>
                    ))}
                  </div>
                )}

                {m.hotlines && m.hotlines.length > 0 && (
                  <div className="mt-2 text-[11px] text-emerald-800 flex items-center gap-1">
                    <PhoneCall className="w-3 h-3" /> Лінія: {m.hotlines.join(", ")}
                  </div>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex items-center gap-2 text-xs text-slate-400 p-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Шукаю у перевіреній базі законів та постанов...
            </div>
          )}
        </div>

        {/* Швидкі запитання для демо */}
        <div className="pt-2 pb-2 flex gap-1.5 overflow-x-auto text-[11px]">
          <button
            onClick={() => handleSend("Які пільги дає статус УБД на комуналку та транспорт?")}
            className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 whitespace-nowrap"
          >
            💡 Пільги УБД на ЖКП
          </button>
          <button
            onClick={() => handleSend("Де у Львові безкоштовно пройти реабілітацію або отримати протез?")}
            className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 whitespace-nowrap"
          >
            💡 Реабілітація Unbroken / Superhumans
          </button>
          <button
            onClick={() => handleSend("Як отримати грант до 1 млн грн на власний бізнес?")}
            className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 whitespace-nowrap"
          >
            💡 Грант «єРобота»
          </button>
        </div>

        {/* Форма введення */}
        <div className="pt-3 border-t border-slate-100 flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Запитайте про виплати, документи, пільги..."
            className="flex-1 p-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
          />
          <button
            onClick={() => handleSend()}
            disabled={isLoading || !input.trim()}
            className="px-5 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white transition disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
