"use client";

import { useState } from "react";
import { MessageSquarePlus, Send, CheckCircle2, AlertCircle } from "lucide-react";

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function FeedbackModal({ isOpen, onClose }: FeedbackModalProps) {
  const [message, setMessage] = useState("");
  const [contact, setContact] = useState("");
  const [name, setName] = useState("");
  const [category, setCategory] = useState("suggestion");
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: message.trim(),
          sender_name: name.trim() || null,
          sender_contact: contact.trim() || null,
          category,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Помилка ${response.status}`);
      }

      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        setMessage("");
        setName("");
        setContact("");
        onClose();
      }, 2500);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Не вдалося надіслати повідомлення. Перевірте підключення до сервера.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 border border-slate-100">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <MessageSquarePlus className="w-5 h-5 text-emerald-600" />
            Зауваження або пропозиція
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl font-bold w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100">
            ✕
          </button>
        </div>

        {success ? (
          <div className="py-10 text-center space-y-3">
            <CheckCircle2 className="w-14 h-14 text-emerald-500 mx-auto" />
            <h3 className="font-bold text-slate-900 text-lg">Дякуємо за відгук!</h3>
            <p className="text-sm text-slate-500">
              Адміністратор платформи обов&apos;язково ознайомиться з вашим повідомленням.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3.5 mt-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Категорія звернення</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 outline-none bg-white"
              >
                <option value="suggestion">💡 Пропозиція щодо покращення платформи</option>
                <option value="bug">🐛 Помилка або неточності в документах</option>
                <option value="partner">🤝 Співпраця / Партнерська програма</option>
                <option value="general">❓ Інше питання</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Ваше зауваження / пропозиція <span className="text-red-500">*</span>
              </label>
              <textarea
                required
                rows={4}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Опишіть, що варто покращити, виправити або додати..."
                className="w-full p-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 outline-none leading-relaxed resize-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Ім&apos;я (необов&apos;язково)</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Ваше ім'я"
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Контакт для зв&apos;язку</label>
                <input
                  type="text"
                  value={contact}
                  onChange={(e) => setContact(e.target.value)}
                  placeholder="Телефон або Telegram"
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500 outline-none"
                />
              </div>
            </div>

            {/* Помилка */}
            {error && (
              <div className="flex items-start gap-2 p-3 bg-red-50 rounded-xl border border-red-200 text-xs text-red-800">
                <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading || !message.trim()}
              className="w-full mt-1 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm transition shadow-md flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  Надсилання...
                </>
              ) : (
                <>
                  Надіслати адміністратору
                  <Send className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
