import { Router } from "express";

const router = Router();

router.get("/", async (_, res) => {
  res.json({
    orders: [],
    statuses: ["Pending", "Paid", "Preparing", "Out for delivery", "Completed"]
  });
});

router.post("/", async (req, res) => {
  const { customerName, phone, email, address, deliveryOption, items } = req.body;
  res.status(201).json({
    message: "Order placed",
    order: { customerName, phone, email, address, deliveryOption, items, status: "Pending" }
  });
});

export default router;
