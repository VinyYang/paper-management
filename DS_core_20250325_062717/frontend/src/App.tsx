import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import { ConfigProvider } from 'antd';

// 导入认证提供者和保护路由组件
import { AuthProvider } from './contexts/AuthContext';
import { SettingsProvider } from './contexts/SettingsContext';
import ProtectedRoute from './components/ProtectedRoute';

// 导入页面组件
import Login from './pages/Login';
import Register from './pages/Register';
import HomePage from './pages/HomePage';
import Library from './pages/Library';
import KnowledgeGraph from './pages/KnowledgeGraph';
import Recommendations from './pages/Recommendations';
import PaperReader from './pages/PaperReader';
import ScihubSearch from './pages/ScihubSearch';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import HeaderComponent from './components/Header';
import Projects from './pages/Projects';
import ProjectDetail from './pages/ProjectDetail';
import PaperSimilarity from './pages/PaperSimilarity';
import About from './pages/About';

const App: React.FC = () => {
  return (
    <ConfigProvider>
      <SettingsProvider>
        <AuthProvider>
          <Router>
            <Routes>
              {/* 公共路由 */}
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/about" element={<About />} />
              
              {/* 受保护的路由 */}
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <Layout style={{ minHeight: '100vh' }}>
                      <HeaderComponent />
                      <Layout.Content style={{ padding: '0', marginTop: 64 }}>
                        <Library />
                      </Layout.Content>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/library" 
                element={
                  <ProtectedRoute>
                    <Layout style={{ minHeight: '100vh' }}>
                      <HeaderComponent />
                      <Layout.Content style={{ padding: '0', marginTop: 64 }}>
                        <Library />
                      </Layout.Content>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/papers/:id" 
                element={
                  <ProtectedRoute>
                    <Layout style={{ minHeight: '100vh' }}>
                      <HeaderComponent />
                      <Layout.Content style={{ padding: '0', marginTop: 64 }}>
                        <PaperReader />
                      </Layout.Content>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/paper-reader/:id" 
                element={
                  <ProtectedRoute>
                    <Layout style={{ minHeight: '100vh' }}>
                      <HeaderComponent />
                      <Layout.Content style={{ padding: '0', marginTop: 64 }}>
                        <PaperReader />
                      </Layout.Content>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/knowledge-graph" 
                element={
                  <ProtectedRoute>
                    <Layout style={{ minHeight: '100vh' }}>
                      <HeaderComponent />
                      <Layout.Content style={{ padding: '0', marginTop: 64 }}>
                        <KnowledgeGraph />
                      </Layout.Content>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/recommendations" 
                element={
                  <ProtectedRoute>
                    <Layout style={{ minHeight: '100vh' }}>
                      <HeaderComponent />
                      <Layout.Content style={{ padding: '0', marginTop: 64 }}>
                        <Recommendations />
                      </Layout.Content>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/scihub-search" 
                element={
                  <ProtectedRoute>
                    <Layout style={{ minHeight: '100vh' }}>
                      <HeaderComponent />
                      <Layout.Content style={{ padding: '0', marginTop: 64 }}>
                        <ScihubSearch />
                      </Layout.Content>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/profile" 
                element={
                  <ProtectedRoute>
                    <Layout style={{ minHeight: '100vh' }}>
                      <HeaderComponent />
                      <Layout.Content style={{ padding: '0', marginTop: 64 }}>
                        <Profile />
                      </Layout.Content>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/settings" 
                element={
                  <ProtectedRoute>
                    <Layout style={{ minHeight: '100vh' }}>
                      <HeaderComponent />
                      <Layout.Content style={{ padding: '0', marginTop: 64 }}>
                        <Settings />
                      </Layout.Content>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/projects" 
                element={
                  <ProtectedRoute>
                    <Layout style={{ minHeight: '100vh' }}>
                      <HeaderComponent />
                      <Layout.Content style={{ padding: '0', marginTop: 64 }}>
                        <Projects />
                      </Layout.Content>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/projects/:id" 
                element={
                  <ProtectedRoute>
                    <Layout style={{ minHeight: '100vh' }}>
                      <HeaderComponent />
                      <Layout.Content style={{ padding: '0', marginTop: 64 }}>
                        <ProjectDetail />
                      </Layout.Content>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/paper-similarity" 
                element={
                  <ProtectedRoute>
                    <Layout style={{ minHeight: '100vh' }}>
                      <HeaderComponent />
                      <Layout.Content style={{ padding: '0', marginTop: 64 }}>
                        <PaperSimilarity />
                      </Layout.Content>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
            </Routes>
          </Router>
        </AuthProvider>
      </SettingsProvider>
    </ConfigProvider>
  );
};

export default App; 