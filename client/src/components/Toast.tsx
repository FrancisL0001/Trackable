// Minimal toast notifications via context.
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { Icon } from "./Icon";

interface ToastContextValue {
  notify: (message: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [message, setMessage] = useState<string | null>(null);

  const notify = useCallback((msg: string) => setMessage(msg), []);

  useEffect(() => {
    if (!message) return;
    const t = setTimeout(() => setMessage(null), 2800);
    return () => clearTimeout(t);
  }, [message]);

  return (
    <ToastContext.Provider value={{ notify }}>
      {children}
      {message && (
        <div
          className="fixed bottom-24 md:bottom-7 left-1/2 -translate-x-1/2 z-[60] flex items-center gap-2 pl-3.5 pr-[18px] py-2.5 rounded-full font-semibold text-sm shadow-lg bg-content text-bg anim-rise"
          role="status"
        >
          <span className="grid place-items-center w-5 h-5 rounded-full bg-primary text-white">
            <Icon name="check" size={12} />
          </span>
          {message}
        </div>
      )}
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within a ToastProvider");
  return ctx;
}
