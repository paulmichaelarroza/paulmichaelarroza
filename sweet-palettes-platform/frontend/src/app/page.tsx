import { motion } from "framer-motion";
import SectionCard from "../components/SectionCard";
import { modules, dbTables, apiGroups } from "../data/platform-data";

const fade = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

export default function HomePage() {
  return (
    <main className="min-h-screen px-6 py-10 md:px-16">
      <motion.header initial="hidden" animate="show" variants={fade} className="card p-8 mb-8">
        <p className="text-sm uppercase tracking-widest text-red-500">Sweet Palettes</p>
        <h1 className="text-4xl md:text-5xl font-extrabold text-red-600 mt-3">Sweet Moments Start Here</h1>
        <p className="mt-4 text-lg max-w-3xl">
          Production-ready platform blueprint for a premium, elegant, AI-powered dessert business.
          Includes public website, ordering, booking, payments, CRM, admin operations, and analytics.
        </p>
      </motion.header>

      <div className="grid lg:grid-cols-2 gap-6">
        <SectionCard title="1) System Architecture Diagram">
          <pre className="text-sm overflow-x-auto bg-white rounded-2xl p-4 border">
{`[Next.js Website + Admin]\n     | REST + JWT\n[Express API Gateway]\n |-- Auth + Roles\n |-- Orders/Bookings\n |-- CRM + Analytics\n |-- AI Orchestrator (OpenAI)\n |-- Messaging Webhooks\n |-- Payment Webhooks\n     |\n[PostgreSQL] [S3/Cloudinary] [Stripe/PayMongo/Xendit]`}
          </pre>
        </SectionCard>

        <SectionCard title="2) UI Layout Plan">
          <ul className="list-disc pl-5 space-y-1">
            <li>Public pages: Home, Services, Pricing, Gallery, Order Online, Book Event, Contact.</li>
            <li>Hero, featured cakes, dessert packages, testimonials, booking CTA, map, socials.</li>
            <li>Rounded cards, soft shadows, warm strawberry-red + cream/pastel palette, feng-shui spacing.</li>
            <li>Floating AI chatbot + Messenger + WhatsApp quick actions.</li>
          </ul>
        </SectionCard>

        <SectionCard title="3) Module Coverage">
          <div className="grid sm:grid-cols-2 gap-2">
            {modules.map((item) => (
              <span key={item} className="rounded-full bg-pink-100 px-3 py-2 text-sm font-semibold">{item}</span>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="4) Database Schema (Core Tables)">
          <div className="grid sm:grid-cols-2 gap-2">
            {dbTables.map((table) => (
              <code key={table} className="rounded-xl bg-green-50 px-3 py-2 text-sm">{table}</code>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="5) API Endpoints">
          <ul className="space-y-1 text-sm">
            {apiGroups.map((api) => (
              <li key={api} className="font-mono rounded-xl bg-peach-50 px-3 py-2">{api}</li>
            ))}
          </ul>
        </SectionCard>

        <SectionCard title="6) AI + Quotation Flow">
          <ol className="list-decimal pl-5 space-y-1">
            <li>Customer submits event details, guest count, budget, and theme.</li>
            <li>AI planner recommends dessert package and estimated cost.</li>
            <li>Quotation service generates editable quote + downloadable PDF.</li>
            <li>Admin reviews, adjusts, and confirms booking/order timeline.</li>
          </ol>
        </SectionCard>
      </div>
    </main>
  );
}
