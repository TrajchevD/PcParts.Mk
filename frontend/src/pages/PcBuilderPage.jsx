import { useEffect, useState } from "react";
import { getBuild, getOptions, setBuildSlot } from "../api/pcBuilder";
import PartsGrid from "../components/pc-builder/PartsGrid";
import BuildSummary from "../components/pc-builder/BuildSummary";
import PartsModel from "../components/pc-builder/PartsModel";

const STEPS = ["cpu", "mb", "ram", "gpu", "storage"];

export default function PcBuilderPage({ buildId }) {
  const [build, setBuild] = useState(null);
  const [step, setStep] = useState(0);
  const [options, setOptions] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeSlot, setActiveSlot] = useState(null);
  const slot = STEPS[step];

  useEffect(() => {
    loadBuild();
  }, [buildId]);

  async function loadBuild() {
    const data = await getBuild(buildId);
    setBuild(data);
  }

  useEffect(() => {
  if (!build) return;

  // getOptions({
  //   slot,
  //   constraints: build.constraints,
  // }).then((res) => {
  //   setOptions(res.items); // ✅ точно
  // });
}, [build, slot]);



  async function handleSelect(productId) {
    await setBuildSlot(buildId, slot, productId);
    await loadBuild();
    setStep((s) => Math.min(s + 1, STEPS.length - 1));
  }

  if (!build) return <div>Loading build...</div>;

  return (
    <div style={{ padding: 20 }}>
      <h2>{build.name}</h2>

      <div style={{ marginBottom: 10 }}>
        {STEPS.map((s, i) => (
          <button
            key={s}
            onClick={() => {
                setStep(i);
                setIsModalOpen(true);
              }}
            style={{
              marginRight: 6,
              fontWeight: i === step ? "bold" : "normal",
            }}
          >
            {s.toUpperCase()}
          </button>
        ))}
      </div>

      {/* <PartsGrid
        options={options}
        slot={slot}
        onSelect={handleSelect}
      /> */}

      {/* <BuildSummary build={build} />
      {isModalOpen && (
          <PartsModel
            slot={slot}
            build={build}
            onClose={() => setIsModalOpen(false)}
            onSelect={async (productId) => {
              await setBuildSlot(buildId, slot, productId);
              await loadBuild();
              setIsModalOpen(false);
            }}
          />
        )} */}
<BuildSummary
  build={build}
  onPick={(slot) => {
    setActiveSlot(slot);
    setIsModalOpen(true);
  }}
  onRemove={async (slot) => {
    await setBuildSlot(buildId, slot, null);
    await loadBuild();
  }}
/>
{isModalOpen && activeSlot && (
  <PartsModel
    slot={activeSlot}
    build={build}
    onClose={() => {
      setIsModalOpen(false);
      setActiveSlot(null);
    }}
    onSelect={async (productId) => {
      await setBuildSlot(buildId, activeSlot, productId);
      await loadBuild();
      setIsModalOpen(false);
      setActiveSlot(null);
    }}
  />
)}


    </div>
  );
}
// function calculateTotalPrice(selectedParts) {
//   return Object.values(selectedParts)
//     .filter(Boolean)
//     .reduce((sum, p) => sum + (p.min_price || 0), 0);
// }