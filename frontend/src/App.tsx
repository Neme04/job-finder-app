import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ThemeProvider } from './lib/theme'
import { AuthProvider } from './lib/auth'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/Layout'
import { AuthPage } from './pages/AuthPage'
import { Criteria } from './pages/Criteria'
import { Feed } from './pages/Feed'
import { Settings } from './pages/Settings'

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/auth" element={<AuthPage />} />
            <Route
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route path="/feed" element={<Feed />} />
              <Route path="/criteria" element={<Criteria />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/" element={<Navigate to="/feed" replace />} />
            </Route>
            <Route path="*" element={<Navigate to="/feed" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
