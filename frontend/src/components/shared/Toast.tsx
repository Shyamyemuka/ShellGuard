"use client";

import { useEffect, useState } from "react";

interface ToastProps {
  message: string;
  type?: "info" | "warning" | "error" | "success";
  duration?: number;
  onClose?: () => void;
}

export function Toast({
  message,
  type = "info",
  duration = 4000,
  onClose,
}: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => onClose?.(), 300); // Wait for fade out animation
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const bgColors = {
    info: "bg-blue-900/90 border-blue-700",
    warning: "bg-yellow-900/90 border-yellow-700",
    error: "bg-red-900/90 border-red-700",
    success: "bg-green-900/90 border-green-700",
  };

  const iconColors = {
    info: "text-blue-400",
    warning: "text-yellow-400",
    error: "text-red-400",
    success: "text-green-400",
  };

  const icons = {
    info: "🛡️",
    warning: "⚠️",
    error: "❌",
    success: "✅",
  };

  return (
    <div
      className={`transition-all duration-300 ${
        isVisible ? "opacity-100 translate-x-0" : "opacity-0 translate-x-4"
      }`}>
      <div
        className={`${bgColors[type]} border rounded-lg px-4 py-3 shadow-lg max-w-md flex items-start gap-3`}>
        <span className={`text-xl ${iconColors[type]}`}>{icons[type]}</span>
        <p className="text-gray-100 text-sm flex-1">{message}</p>
        <button
          onClick={() => {
            setIsVisible(false);
            setTimeout(() => onClose?.(), 300);
          }}
          className="text-gray-400 hover:text-gray-200 ml-2">
          ✕
        </button>
      </div>
    </div>
  );
}
