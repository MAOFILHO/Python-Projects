import { Navigate, Route, Routes } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { OverviewPage } from './pages/OverviewPage';
import { MigrationPage } from './pages/MigrationPage';
import { OperationsPage } from './pages/OperationsPage';
import { ServiceHealthPage } from './pages/ServiceHealthPage';
import { PerformanceComparePage } from './pages/PerformanceComparePage';
import { RecentHistoryPage } from './pages/RecentHistoryPage';
import { LearnPage } from './pages/learn/LearnPage';
import './theme/contoso.css';
import './theme/layout.css';

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/migration" element={<MigrationPage />} />
        <Route path="/operations" element={<OperationsPage />} />
        <Route path="/health" element={<ServiceHealthPage />} />
        <Route path="/compare" element={<PerformanceComparePage />} />
        <Route path="/history" element={<RecentHistoryPage />} />
        <Route path="/learn" element={<LearnPage />} />
        {/* Old per-section Learn/Glossary routes now redirect into the single
            consolidated Learn page, at the matching in-page anchor. */}
        <Route path="/glossary" element={<Navigate to="/learn#glossary" replace />} />
        <Route path="/learn/what-are-microservices" element={<Navigate to="/learn" replace />} />
        <Route path="/learn/strangler-fig" element={<Navigate to="/learn#strangler-fig" replace />} />
        <Route path="/learn/service-boundaries" element={<Navigate to="/learn#service-boundaries" replace />} />
        <Route path="/learn/observability" element={<Navigate to="/learn#observability" replace />} />
        <Route path="/learn/when-not-to-use" element={<Navigate to="/learn#when-not-to-use" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;
