import { X } from "lucide-react";
import { useEffect } from "react";


export default function Modal({
  open,
  title,
  subtitle,
  children,
  onClose,
  size = "medium",
}) {
  useEffect(() => {
    if (!open) {
      return undefined;
    }

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    document.body.style.overflow = "hidden";

    window.addEventListener(
      "keydown",
      handleKeyDown,
    );

    return () => {
      document.body.style.overflow = "";

      window.removeEventListener(
        "keydown",
        handleKeyDown,
      );
    };
  }, [open, onClose]);


  if (!open) {
    return null;
  }


  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <section
        className={`modal-card modal-${size}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <header className="modal-header">
          <div>
            <span className="card-kicker">
              SmartInvoice
            </span>

            <h2>{title}</h2>

            {subtitle && (
              <p>{subtitle}</p>
            )}
          </div>

          <button
            className="modal-close-button"
            type="button"
            aria-label="Cerrar"
            onClick={onClose}
          >
            <X size={19} />
          </button>
        </header>

        <div className="modal-body">
          {children}
        </div>
      </section>
    </div>
  );
}
