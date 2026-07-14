// Accessible modal dialog: closes on overlay click and Escape.
import { useEffect, type ReactNode } from "react";
import { Icon } from "./Icon";

interface ModalProps {
  title: string;
  onClose: () => void;
  children: ReactNode;
}

export function Modal({ title, onClose, children }: ModalProps) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center p-4 bg-[var(--overlay)] backdrop-blur-[2px] anim-fade"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="w-full max-w-[540px] max-h-[90vh] overflow-y-auto bg-surface rounded-lg border border-border shadow-lg anim-pop"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between pl-5 pr-4 py-4 border-b border-border sticky top-0 bg-surface rounded-t-lg">
          <h3 className="text-lg m-0">{title}</h3>
          <button className="icon-btn !w-9 !h-9" onClick={onClose} aria-label="Close dialog">
            <Icon name="close" size={17} />
          </button>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
}
