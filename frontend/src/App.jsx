import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import ToastContainer from './components/ui/Toast';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Login from './components/auth/Login';
import Dashboard from './pages/Dashboard';
import Courses from './pages/Courses';
import NewCourse from './pages/NewCourse';
import CourseDetail from './pages/CourseDetail';
import StudyPlan from './pages/StudyPlan';
import Quiz from './pages/Quiz';
import Progress from './pages/Progress';
import QA from './pages/QA';
import CodeEditor from './pages/CodeEditor';
import './index.css';

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <ToastContainer />
          <Routes>
            <Route path="/" element={<Login />} />

            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />

            <Route path="/courses" element={
              <ProtectedRoute>
                <Courses />
              </ProtectedRoute>
            } />

            <Route path="/courses/new" element={
              <ProtectedRoute>
                <NewCourse />
              </ProtectedRoute>
            } />

            <Route path="/courses/:id" element={
              <ProtectedRoute>
                <CourseDetail />
              </ProtectedRoute>
            } />

            <Route path="/study-plan" element={
              <ProtectedRoute>
                <StudyPlan />
              </ProtectedRoute>
            } />

            <Route path="/quiz" element={
              <ProtectedRoute>
                <Quiz />
              </ProtectedRoute>
            } />

            <Route path="/progress" element={
              <ProtectedRoute>
                <Progress />
              </ProtectedRoute>
            } />

            <Route path="/qa" element={
              <ProtectedRoute>
                <QA />
              </ProtectedRoute>
            } />

            <Route path="/code-editor" element={
              <ProtectedRoute>
                <CodeEditor />
              </ProtectedRoute>
            } />

            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
