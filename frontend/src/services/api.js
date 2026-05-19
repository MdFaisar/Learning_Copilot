import axios from 'axios';
import { auth } from '../config/firebase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
    const user = auth.currentUser;
    if (user) {
        const token = await user.getIdToken();
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Courses
export const getCourses = () => api.get('/courses');
export const getCourse = (id) => api.get(`/courses/${id}`);
export const createCourse = (data) => api.post('/courses', data);
export const updateCourse = (id, data) => api.put(`/courses/${id}`, data);
export const deleteCourse = (id) => api.delete(`/courses/${id}`);
export const uploadMaterial = (courseId, formData) =>
    api.post(`/courses/${courseId}/materials`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
export const processMaterials = (courseId) => api.post(`/courses/${courseId}/process`);

// Study Plans
export const generateStudyPlan = (data) => api.post('/study-plans/generate', data);
export const getStudyPlan = (courseId) => api.get(`/study-plans/${courseId}`);
export const updateStudyPlan = (planId, data) => api.put(`/study-plans/${planId}`, data);
export const adjustStudyPlan = (planId) => api.post(`/study-plans/${planId}/adjust`);

// Quiz
export const generateQuiz = (data) => api.post('/quiz/generate', data);
export const submitQuiz = (data) => api.post('/quiz/submit', data);
export const getQuizHistory = (courseId) => api.get(`/quiz/history/${courseId}`);

// Q&A
export const askQuestion = (data) => api.post('/qa/query', data);
export const getQAHistory = (courseId) => api.get(`/qa/history/${courseId}`);
export const deleteQAHistory = (courseId) => api.delete(`/qa/history/${courseId}/clear`);

// Progress
export const getProgress = (courseId) => api.get(`/progress/${courseId}`);
export const logStudySession = (data) => api.post('/progress/session', data);
export const updateMastery = (data) => api.put('/progress/mastery', data);

// Code Editor
export const getSupportedLanguages = () => api.get('/code/languages');
export const executeCode = (data) => api.post('/code/execute', data);
export const debugCode = (data) => api.post('/code/debug', data);
export const explainCodeAPI = (data) => api.post('/code/explain', data);
export const improveCodeAPI = (data) => api.post('/code/improve', data);
export const generateTestCases = (data) => api.post('/code/test-cases', data);

export default api;
