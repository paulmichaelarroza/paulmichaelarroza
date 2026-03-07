import { Router } from "express";

const router = Router();

router.post("/generate", (req, res) => {
  const { guestCount = 50, eventType = "Event", packageTier = "Standard" } = req.body;
  const perGuest = packageTier === "Premium" ? 16 : 10;
  const subtotal = guestCount * perGuest;
  const delivery = subtotal > 500 ? 0 : 25;
  res.json({
    eventType,
    packageTier,
    lineItems: [
      { item: "Dessert package", qty: guestCount, unitPrice: perGuest, total: subtotal }
    ],
    delivery,
    totalEstimate: subtotal + delivery
  });
});

export default router;
