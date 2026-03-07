export async function generateCakeDesigns({ eventType, theme, colorPalette, cakeSize, flavor }) {
  return {
    promptSummary: { eventType, theme, colorPalette, cakeSize, flavor },
    concepts: [
      "Floral buttercream with pearl accents",
      "Minimalist pastel tiers with gold leaf",
      "Modern textured fondant with sugar blooms"
    ],
    note: "Connect OpenAI + image generation provider to return rendered concept images."
  };
}

export async function planEventDesserts({ eventType, guestCount, budget, theme }) {
  return {
    eventType,
    guestCount,
    budget,
    theme,
    recommendation: [
      { item: "Signature Cake", qty: 1 },
      { item: "Mini Cupcakes", qty: Math.ceil(guestCount * 1.5) },
      { item: "Dessert Shots", qty: guestCount },
      { item: "Macarons", qty: Math.ceil(guestCount * 0.8) }
    ],
    estimatedCost: Math.round(guestCount * 12)
  };
}
