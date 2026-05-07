export const storeLogos = {
  anhoch: "/logos/anhoch.png",
  setec: "/logos/setec.png",
  neptun: "/logos/neptun.png",
  gjirafa50: "/logos/gjirafa50.png",
};

// fallback if missing
export function getStoreLogo(store) {
  if (!store) return "/logos/default.png";

  const key = store.toLowerCase().trim();
  return storeLogos[key] || "/logos/default.png";
}
