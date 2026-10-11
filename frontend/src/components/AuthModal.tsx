"use client";

import { useState } from "react";
import { LogIn, UserCheck, Phone, Lock, User, ArrowRight } from "lucide-react";
import { fetchApi } from "@/lib/api";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (data: { user_token: string; phone: string; full_name?: string }) => void;
}

export default function AuthModal({ isOpen, onClose, onSuccess }: AuthModalProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const existingToken = localStorage.getItem("veteran_token") || undefined;
      const endpoint = mode === "register" ? "/auth/register" : "/auth/login";
      const payload = mode === "register"
        ? { phone, password, full_name: fullName || undefined, existing_token: existingToken }
        : { phone, password };

      const res = await fetchApi(endpoint, {
        method: "POST",
        body: JSON.stringify(payload),
      });

      localStorage.setItem("veteran_token", res.user_token);
      localStorage.setItem("veteran_phone", res.phone);
      if (res.full_name) localStorage.setItem("veteran_name", res.full_name);

      onSuccess(res);
      onClose();
    } catch (err: any) {
      setError(err.message || "Помилка авторизації. Перевірте дані.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 sm:p-8 border border-slate-100">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-emerald-600" />
            {mode === "login" ? "Вхід до особистого плану" : "Реєстрація акаунта"}
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-lg font-bold">
            ✕
          </button>
        </div>

        <p className="text-xs text-slate-500 mt-2 mb-4 leading-relaxed">
          {mode === "login"
            ? "Увійдіть за номером телефону, щоб бачити свій прогрес як на комп'ютері, так і на смартфоні."
            : "Зареєструйтеся, щоб ваш персональний план та збережені кроки були доступні на будь-якому пристрої."}
        </p>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          {mode === "register" && (
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Ваше ім'я / позивний</label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Андрій"
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Номер телефону</label>
            <div className="relative">
              <Phone className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="tel"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+380 97 123 45 67"
                className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Пароль</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Введіть ваш пароль"
                className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full mt-2 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm transition shadow-md flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {isLoading ? "Зачекайте..." : mode === "login" ? "Увійти" : "Зареєструватися"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-5 pt-4 border-t border-slate-100 text-center">
          {mode === "login" ? (
            <p className="text-xs text-slate-600">
              Ще не маєте акаунта?{" "}
              <button
                type="button"
                onClick={() => { setMode("register"); setError(""); }}
                className="text-emerald-700 font-bold hover:underline"
              >
                Створити акаунт
              </button>
            </p>
          ) : (
            <p className="text-xs text-slate-600">
              Вже зареєстровані?{" "}
              <button
                type="button"
                onClick={() => { setMode("login"); setError(""); }}
                className="text-emerald-700 font-bold hover:underline"
              >
                Увійти
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
