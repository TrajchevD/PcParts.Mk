import { Routes, Route, Navigate, useParams } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import CpuProductsPage from "./pages/CpuProductsPage";
import GpuProductsPage from "./pages/GpuProductsPage";
import MbProductsPage from "./pages/MbProductsPage";
import RamProductsPage from "./pages/RamProductsPage";
import StorageProductsPage from "./pages/StorageProductsPage";
import PcBuilderV2Page from "./pages/PcBuilderV2Page";
import ComparePage from "./pages/ComparePage";
import BuildManagerPage from "./pages/BuildManagerPage";
import RecommendationPage from "./pages/RecommendationPage";

// Map old /category/:slug routes to new /catalog/:slug pages
const CATALOG_MAP = {
  cpu: "/catalog/cpu",
  gpu: "/catalog/gpu",
  mb: "/catalog/mb",
  ram: "/catalog/ram",
  storage: "/catalog/storage",
};

function CategoryRedirect() {
  const { category } = useParams();
  const dest = CATALOG_MAP[category] ?? "/";
  return <Navigate to={dest} replace />;
}

function PcBuilderV2Wrapper() {
  const { buildId } = useParams();
  return <PcBuilderV2Page buildId={Number(buildId)} />;
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />

        {/* Legacy category routes → redirect to new catalog pages */}
        <Route path="/category/:category" element={<CategoryRedirect />} />

        {/* Catalogs */}
        <Route path="/catalog/cpu"     element={<CpuProductsPage />} />
        <Route path="/catalog/gpu"     element={<GpuProductsPage />} />
        <Route path="/catalog/mb"      element={<MbProductsPage />} />
        <Route path="/catalog/ram"     element={<RamProductsPage />} />
        <Route path="/catalog/storage" element={<StorageProductsPage />} />

        {/* Builder — /builder/:buildId redirects to /builder-v2/:buildId */}
        <Route
          path="/builder/:buildId"
          element={<BuilderV1Redirect />}
        />
        <Route path="/builder-v2/:buildId" element={<PcBuilderV2Wrapper />} />
        <Route path="/builds"              element={<BuildManagerPage />} />

        {/* Tools */}
        <Route path="/recommend" element={<RecommendationPage />} />
        <Route path="/compare"   element={<ComparePage />} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

function BuilderV1Redirect() {
  const { buildId } = useParams();
  return <Navigate to={`/builder-v2/${buildId}`} replace />;
}
