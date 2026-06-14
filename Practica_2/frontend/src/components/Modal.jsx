import { useEffect } from "react";


function Modal({
  open,
  title,
  children,
  onClose,
  footer,
  size = "medium",
}) {
  useEffect(() => {
    if (!open) {
      return undefined;
    }

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    document.addEventListener(
      "keydown",
      handleKeyDown
    );

    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener(
        "keydown",
        handleKeyDown
      );

      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div
      className="modal-overlay"
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
        aria-labelledby="modal-title"
      >
        <header className="modal-header">
          <h2 id="modal-title">{title}</h2>

          <button
            type="button"
            className="icon-button"
            onClick={onClose}
            aria-label="Cerrar ventana"
          >
            ×
          </button>
        </header>

        <div className="modal-body">
          {children}
        </div>

        {footer && (
          <footer className="modal-actions">
            {footer}
          </footer>
        )}
      </section>
    </div>
  );
}


export default Modal;
