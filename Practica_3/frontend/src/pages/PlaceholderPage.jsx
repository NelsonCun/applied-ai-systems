import {
  Construction,
} from "lucide-react";


export default function PlaceholderPage({
  title,
  description,
}) {
  return (
    <div>
      <header className="page-header">
        <div>
          <p className="eyebrow">
            SmartInvoice
          </p>

          <h1>{title}</h1>

          <p>{description}</p>
        </div>
      </header>

      <section className="content-card placeholder-card">
        <Construction size={42} />

        <h2>Módulo preparado</h2>

        <p>
          La ruta y la navegación ya están
          disponibles. La interfaz funcional
          se incorporará en el siguiente
          bloque.
        </p>
      </section>
    </div>
  );
}
