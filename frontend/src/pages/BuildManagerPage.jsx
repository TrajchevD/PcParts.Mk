import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getUserBuilds, deleteBuild, renameBuild, createBuild } from "../api/buildManager";
import { useAuth } from "../auth/AuthContext";
import { useToast } from "../components/Toast";

export default function BuildManagerPage() {
  const [builds, setBuilds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();
  const { token } = useAuth();
  const toast = useToast();

  async function load() {
    setLoading(true);
    try {
      const data = await getUserBuilds();
      setBuilds(Array.isArray(data) ? data : (data?.builds ?? []));
    } catch (e) {
      toast.error(e.message || "Failed to load builds.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleRename(id, newName) {
    if (!newName.trim()) return;
    try {
      await renameBuild(id, newName);
      await load();
      toast.success("Build renamed.");
    } catch (e) {
      toast.error(e.message || "Rename failed.");
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this build?")) return;
    try {
      await deleteBuild(id);
      await load();
      toast.success("Build deleted.");
    } catch (e) {
      toast.error(e.message || "Delete failed.");
    }
  }

  async function handleNewBuild() {
    if (creating) return;
    setCreating(true);
    try {
      const data = await createBuild("New Build");
      navigate(`/builder-v2/${data.build_id}`);
    } catch (e) {
      toast.error(e.message || "Failed to create build.");
    } finally {
      setCreating(false);
    }
  }

  if (!token) {
    return (
      <div className="build-manager-page">
        <div className="empty-state">
          <span className="empty-icon">🔐</span>
          <h3>Login required</h3>
          <p>Sign in to view and manage your saved builds.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="build-manager-page">
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
        <h2 className="builder-title">My Builds</h2>
        <button className="btn-primary" onClick={handleNewBuild} disabled={creating}>
          {creating ? <><span className="loading-spinner" /> Creating…</> : "+ New Build"}
        </button>
      </div>

      {loading ? (
        <div className="loading-page">
          <span className="loading-spinner" />
          <span>Loading your builds…</span>
        </div>
      ) : builds.length === 0 ? (
        <div className="empty-state" style={{ marginTop: 40 }}>
          <span className="empty-icon">🖥️</span>
          <h3>No builds yet</h3>
          <p>Create your first PC build to get started.</p>
          <button className="btn-primary" style={{ marginTop: 8 }} onClick={handleNewBuild} disabled={creating}>
            + Create Build
          </button>
        </div>
      ) : (
        <div className="build-manager-grid">
          {builds.map(b => (
            <BuildCard
              key={b.build_id}
              build={b}
              onOpen={() => navigate(`/builder-v2/${b.build_id}`)}
              onRename={handleRename}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function BuildCard({ build, onOpen, onRename, onDelete }) {
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(build.name);

  return (
    <div className="build-manager-card">
      {editing ? (
        <>
          <input
            value={name}
            autoFocus
            onChange={e => setName(e.target.value)}
            onKeyDown={e => {
              if (e.key === "Enter")  { onRename(build.build_id, name); setEditing(false); }
              if (e.key === "Escape") { setEditing(false); setName(build.name); }
            }}
          />
          <div className="build-manager-actions">
            <button onClick={() => { onRename(build.build_id, name); setEditing(false); }}>Save</button>
            <button onClick={() => { setEditing(false); setName(build.name); }}>Cancel</button>
          </div>
        </>
      ) : (
        <>
          <div className="build-manager-name">{build.name}</div>
          {build.created_at && (
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: -8 }}>
              {new Date(build.created_at).toLocaleDateString()}
            </div>
          )}
          <div className="build-manager-actions">
            <button onClick={onOpen}>Open</button>
            <button onClick={() => setEditing(true)}>Rename</button>
            <button className="danger" onClick={() => onDelete(build.build_id)}>Delete</button>
          </div>
        </>
      )}
    </div>
  );
}
