"use client";

import { useState } from "react";
import { MessageSquarePlus, Send, CheckCircle2 } from "lucide-react";
import { fetchApi } from "@/lib/api";

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function FeedbackModal({ isOpen, onClose }: FeedbackModalProps) {
  const [message, setMessage] = useState("");
  const [contact, setContact] = useState("");
  const [name, setName] = useState("");
  const [category, setCategory] = useState("suggestion");
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    setIsLoading(true);

    try {
      await fetchApi("/feedback", {
        method: "POST",
        body: JSON.stringify({
          message,
          sender_name: name || undefined,
          sender_contact: contact || undefined,
          category,
        }),
      });

      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        setMessage("");
        onClose();
      }, 2500);
    } catch (err) {
      console.error(err);
      alert("Не вдалося надіслати повідомлення. Спробуйте пізніше.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 sm:p-8 border border-slate-100">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <MessageSquarePlus className="w-5 h-5 text-emerald-600" />
            Зауваження або пропозиція
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-lg font-bold">
            ✕
          </button>
        </div>

        {success ? (
          <div className="py-8 text-center space-y-2">
            <CheckCircle2 className="w-12 h-12 text-emerald-600 mx-auto" />
            <h3 className="font-bold text-slate-900">Дякуємо за ваш відгук!</h3>
            <p className="text-xs text-slate-500">
              Адміністратор платформи та координатори обов'язково ознайомляться з вашим повідомленням.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3.5 mt-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Категорія звернення</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
              >
                <option value="suggestion">💡 Пропозиція щодо покращення платформи</option>
                <option value="bug">🐛 Помилка або неточності в документах</option>
                <option value="partner">🤝 Співпраця / Партнерська програма</option>
                <option value="general">❓ Інше питання</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Ваше зауваження / пропозиція</label>
              <textarea
                required
                rows={3}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Опишіть, що варто покращити, виправити або додати..."
                className="w-full p-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 outline-none leading-relaxed"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Ім'я (необов'язково)</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Ваше ім'я"
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Контакт для зв'язку</label>
                <input
                  type="text"
                  value={contact}
                  onChange={(e) => setContact(e.target.value)}
                  placeholder="Телефон або Telegram"
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500 outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || !message.trim()}
              className="w-full mt-2 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm transition shadow-md flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isLoading ? "Надсилання..." : "Надіслати адміністратору"}
              <Send className="w-4 h-4" />
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
