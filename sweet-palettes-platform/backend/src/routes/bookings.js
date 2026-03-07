import { Router } from "express";
import multer from "multer";

const router = Router();
const upload = multer({ limits: { fileSize: 10 * 1024 * 1024 } });

router.post("/", upload.array("attachments", 3), (req, res) => {
  const booking = req.body;
  res.status(201).json({
    message: "Booking request submitted",
    booking,
    attachments: req.files?.map((f) => ({ name: f.originalname, size: f.size })) || []
  });
});

export default router;
