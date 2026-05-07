import { useEffect, useState, useCallback } from "react";
import { useOutletContext } from "react-router-dom";
import { getBuildV2, setBuildSlot, removeBuildSlot } from "../api/pcBuilderV2";
import { renameBuild } from "../api/buildManager";
import { useToast } from "../components/Toast";

import CpuPicker from "../components/cpu/CpuPicker";
import GpuPicker from "../components/gpu/GpuPicker";
import MbPicker from "../components/mb/MbPicker";
import RamPicker from "../components/ram/RamPicker";
import StoragePicker from "../components/storage/StoragePicker";
import PartsModalV2 from "../components/pc-builder/PartsModalV2";
import BuildSummaryV2 from "../components/pc-builder/BuildSummaryV2";

const SLOT_DEFS = [
  { key: "cpu",     label: "CPU",         emoji: "⬡", iconCls: "mob-slot-icon-cpu"     },
  { key: "mb",      label: "Motherboard", emoji: "⊞", iconCls: "mob-slot-icon-mb"      },
  { key: "ram",     label: "RAM",         emoji: "≡", iconCls: "mob-slot-icon-ram"      },
  { key: "gpu",     label: "GPU",         emoji: "▣", iconCls: "mob-slot-icon-gpu"      },
  { key: "storage", label: "Storage",     emoji: "◧", iconCls: "mob-slot-icon-storage"  },
];

function getPartName(part) {
  if (!part) return null;
  const s = part.specs || {};
  return part.title || s.cpu_model || s.gpu_model || s.mb_model || s.series || "Unknown";
}

export default function PcBuilderV2Page({ buildId }) {
  const { toggleSidebar } = useOutletContext() || {};
  const toast = useToast();
  const [build, setBuild] = useState(null);
  const [loading, setLoading] = useState(true);
  const [slotLoading, setSlotLoading] = useState(false);
  const [activeSlot, setActiveSlot] = useState(null);
  const [editingName, setEditingName] = useState(false);
  const [tempName, setTempName] = useState("");
  const [error, setError] = useState("");

  const loadBuild = useCallback(async () => {
    try {
      const data = await getBuildV2(buildId);
      setBuild(data);
      setTempName(data.name);
    } catch (e) {
      setError(e.message || "Failed to load build.");
    } finally {
      setLoading(false);
    }
  }, [buildId]);

  useEffect(() => { loadBuild(); }, [loadBuild]);

  async function handleRename() {
    if (!tempName.trim()) return;
    try {
      await renameBuild(buildId, tempName);
      await loadBuild();
      setEditingName(false);
      toast.success("Build renamed.");
    } catch (e) {
      toast.error(e.message || "Rename failed.");
    }
  }

  async function handleSlotSelect(slot, productId) {
    setSlotLoading(true);
    setError("");
    try {
      await setBuildSlot(buildId, slot, productId);
      await loadBuild();
      setActiveSlot(null);
    } catch (e) {
      const msg = e.message || "Compatibility issue.";
      setError(msg);
      toast.error(msg);
    } finally {
      setSlotLoading(false);
    }
  }

  async function handleRemove(slot) {
    setSlotLoading(true);
    try {
      await removeBuildSlot(buildId, slot);
      await loadBuild();
      toast.info("Component removed.");
    } catch (e) {
      toast.error(e.message || "Failed to remove component.");
    } finally {
      setSlotLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="builder-loading">
        <span className="loading-spinner" />
        Loading build…
      </div>
    );
  }

  if (!build) {
    return (
      <div className="build-manager-page">
        <div className="empty-state">
          <span className="empty-icon">⚠️</span>
          <h3>Build not found</h3>
          <p>{error || "This build could not be loaded."}</p>
        </div>
      </div>
    );
  }

  const totalPrice = Object.values(build.parts).reduce((sum, p) => sum + (p?.best_price ?? 0), 0);
  const filledCount = SLOT_DEFS.filter(s => build.parts[s.key]).length;
  const compatErrors = build.constraints?.errors ?? [];

  return (
    <>
      {/* ── DESKTOP ── */}
      <div className="builder-page dsk-only">
        <div className="builder-header">
          {editingName ? (
            <>
              <input
                value={tempName}
                autoFocus
                onChange={e => setTempName(e.target.value)}
                onKeyDown={e => {
                  if (e.key === "Enter")  handleRename();
                  if (e.key === "Escape") { setEditingName(false); setTempName(build.name); }
                }}
              />
              <button className="btn-primary small" onClick={handleRename}>Save</button>
              <button className="btn-text" onClick={() => { setEditingName(false); setTempName(build.name); }}>Cancel</button>
            </>
          ) : (
            <>
              <h2 className="builder-title">{build.name}</h2>
              <button
                className="btn-text"
                style={{ fontSize: "1.1rem", padding: "4px 8px" }}
                title="Rename build"
                onClick={() => setEditingName(true)}
              >
                ✏
              </button>
            </>
          )}
          {slotLoading && <span className="loading-spinner" style={{ marginLeft: 8 }} />}
        </div>

        {error && <div className="compat-error" style={{ marginBottom: 12 }}>⚠️ {error}</div>}

        <div className="builder-layout">
          <div className="builder-slots">
            <BuildSummaryV2 build={build} onPick={setActiveSlot} onRemove={handleRemove} />
          </div>
          <div className="builder-side-panel">
            <div className="compat-panel">
              <h3>Compatibility</h3>
              {compatErrors.length ? (
                <div className="compat-error-box">
                  {compatErrors.map((e, i) => <div key={i}>• {e}</div>)}
                </div>
              ) : (
                <div className="compat-ok">✓ All components compatible</div>
              )}
            </div>
            <div className="builder-total">
              <div>Total Build Price</div>
              <div className="builder-total-price">{totalPrice.toLocaleString()} ден</div>
            </div>
          </div>
        </div>
      </div>

      {/* ── MOBILE ── */}
      <div className="mob-builder mob-only">
        {/* Top bar */}
        <div className="mob-topbar">
          <span className="mob-page-title">PC Builder</span>
          <div className="mob-topbar-right">
            <button className="mob-icon-btn">↑</button>
            <button className="mob-icon-btn mob-icon-btn-accent" onClick={toggleSidebar}>☰</button>
          </div>
        </div>

        {error && <div className="compat-error" style={{ margin: "0 16px 8px" }}>⚠️ {error}</div>}

        {/* Progress */}
        <div className="mob-progress">
          <div className="mob-progress-row">
            <span className="mob-progress-lbl">Progress</span>
            <span className="mob-progress-count">{filledCount} / 5 slots filled</span>
          </div>
          <div className="mob-progress-track">
            <div className="mob-progress-fill" style={{ width: `${(filledCount / 5) * 100}%` }} />
          </div>
        </div>

        {/* Slot cards */}
        {SLOT_DEFS.map(slot => {
          const part = build.parts[slot.key];
          const filled = !!part;
          const name = getPartName(part);
          const price = part?.best_price;
          const isStorage = slot.key === "storage";

          let cardCls = "mob-slot-card";
          if (filled) cardCls += " mob-slot-card-filled";
          else        cardCls += " mob-slot-card-empty";

          return (
            <div key={slot.key} className={cardCls} onClick={() => setActiveSlot(slot.key)}>
              <div className={`mob-slot-icon ${slot.iconCls}${isStorage && !filled ? " mob-slot-icon-storage-empty" : ""}`}>
                {slot.emoji}
              </div>
              <div className="mob-slot-body">
                <span className="mob-slot-cat">{slot.label}</span>
                {filled ? (
                  <>
                    <span className="mob-slot-name">{name}</span>
                    <span className={`mob-slot-compat mob-slot-compat-ok`}>✓ Compatible</span>
                  </>
                ) : (
                  <span className="mob-slot-empty-hint">Tap to add {slot.label.toLowerCase()}…</span>
                )}
              </div>
              <div className="mob-slot-right">
                {filled && price != null ? (
                  <>
                    <span className="mob-slot-price">{price.toLocaleString()}</span>
                    <span className="mob-slot-den">ден</span>
                  </>
                ) : (
                  <button className="mob-slot-add" onClick={e => { e.stopPropagation(); setActiveSlot(slot.key); }}>+</button>
                )}
              </div>
            </div>
          );
        })}

        {/* Build summary */}
        <div className="mob-build-summary">
          <div className="mob-summary-top">
            <div>
              <div className="mob-summary-lbl">Partial total</div>
              <div className="mob-summary-price">
                {totalPrice.toLocaleString()} <span className="mob-summary-den">ден</span>
              </div>
            </div>
          </div>

          <div className="mob-compat-list">
            {compatErrors.length > 0
              ? compatErrors.map((e, i) => (
                  <div key={i} className="mob-compat-alert mob-compat-warn">
                    <span>⚠</span><span>{e}</span>
                  </div>
                ))
              : (
                <div className="mob-compat-alert mob-compat-ok">
                  <span>✓</span><span>All components compatible</span>
                </div>
              )
            }
          </div>

          <div className="mob-summary-btns">
            <button className="mob-btn-accent" style={{ flex: 1 }}>Save Build</button>
            <button className="mob-btn-default" style={{ flex: 1 }}>Export PDF</button>
          </div>
        </div>
      </div>

      {/* Part picker modals — shared between mobile and desktop */}
      {activeSlot === "cpu" && (
        <PartsModalV2 title="Select CPU" onClose={() => setActiveSlot(null)}>
          <CpuPicker buildId={buildId} onSelect={id => handleSlotSelect("cpu", id)} />
        </PartsModalV2>
      )}
      {activeSlot === "gpu" && (
        <PartsModalV2 title="Select GPU" onClose={() => setActiveSlot(null)}>
          <GpuPicker buildId={buildId} onSelect={id => handleSlotSelect("gpu", id)} />
        </PartsModalV2>
      )}
      {activeSlot === "mb" && (
        <PartsModalV2 title="Select Motherboard" onClose={() => setActiveSlot(null)}>
          <MbPicker onSelect={id => handleSlotSelect("mb", id)} />
        </PartsModalV2>
      )}
      {activeSlot === "ram" && (
        <PartsModalV2 title="Select RAM" onClose={() => setActiveSlot(null)}>
          <RamPicker onSelect={id => handleSlotSelect("ram", id)} />
        </PartsModalV2>
      )}
      {activeSlot === "storage" && (
        <PartsModalV2 title="Select Storage" onClose={() => setActiveSlot(null)}>
          <StoragePicker onSelect={id => handleSlotSelect("storage", id)} />
        </PartsModalV2>
      )}
    </>
  );
}
