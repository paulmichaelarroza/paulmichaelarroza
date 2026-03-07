import { ReactNode } from "react";

export default function SectionCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="card p-6 md:p-8">
      <h3 className="text-xl font-bold text-red-600 mb-3">{title}</h3>
      {children}
    </section>
  );
}
