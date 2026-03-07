import { Router } from "express";
import { generateCakeDesigns, planEventDesserts } from "../services/aiService.js";

const router = Router();

router.post("/cake-design", async (req, res) => {
  const result = await generateCakeDesigns(req.body);
  res.json(result);
});

router.post("/event-plan", async (req, res) => {
  const result = await planEventDesserts(req.body);
  res.json(result);
});

export default router;
