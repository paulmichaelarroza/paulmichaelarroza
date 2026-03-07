import express from "express";
import cors from "cors";
import rateLimit from "express-rate-limit";
import dotenv from "dotenv";
import orderRoutes from "./routes/orders.js";
import bookingRoutes from "./routes/bookings.js";
import aiRoutes from "./routes/ai.js";
import quotationRoutes from "./routes/quotations.js";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json({ limit: "2mb" }));
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 300 }));

app.get("/health", (_, res) => res.json({ ok: true, service: "sweet-palettes-api" }));
app.use("/api/orders", orderRoutes);
app.use("/api/bookings", bookingRoutes);
app.use("/api/ai", aiRoutes);
app.use("/api/quotations", quotationRoutes);

app.listen(process.env.PORT || 4000, () => {
  console.log("Sweet Palettes API running");
});
