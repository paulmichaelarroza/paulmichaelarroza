# Sweet Palettes Platform

Production-ready starter architecture for **Sweet Palettes** — *Sweet Moments Start Here*.

## Included Deliverables

1. **System architecture diagram**: in `frontend/src/app/page.tsx`
2. **UI layout plan**: homepage architecture section
3. **Database schema**: `db/schema.sql`
4. **API endpoints**: listed in `frontend/src/data/platform-data.ts` and implemented in backend routes
5. **Frontend code examples**: Next.js + Tailwind + Framer Motion scaffold
6. **Backend code examples**: Express API with modules for orders, bookings, AI, quotations
7. **AI modules**: `backend/src/services/aiService.js`
8. **CRM module base**: represented in schema (`customers`, `messages`, `bookings`, `orders`) and admin-ready API architecture
9. **Payment integration base**: schema + status workflow for Stripe/PayMongo/Xendit expansion
10. **Deployment guide**: steps below

## Deployment Guide

### Frontend (Vercel)
1. `cd frontend`
2. `npm install`
3. `npm run build`
4. Deploy to Vercel with environment variable `NEXT_PUBLIC_API_BASE_URL`

### Backend (Render/Railway/Fly.io)
1. `cd backend`
2. `npm install`
3. Set `.env` values (`PORT`, `JWT_SECRET`, `DATABASE_URL`, `OPENAI_API_KEY`)
4. Run `npm run dev` (replace with production process manager)

### Database (PostgreSQL)
1. Provision PostgreSQL
2. Run `db/schema.sql`
3. Add indexes and migrations via your migration tool (Prisma/Knex/Drizzle)

### Storage
Use Cloudinary or AWS S3 for booking attachments and gallery assets.

## Security Checklist
- JWT-based auth with role checks
- Rate limiting enabled
- File upload size limit 10MB
- Input validation/sanitization to be added on each route
- Payment webhooks must verify signatures
