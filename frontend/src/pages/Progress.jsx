import React, { useState, useEffect } from 'react';
import Navbar from '../components/layout/Navbar';
import { getCourses, getProgress } from '../services/api';
import { TrendingUp, Award, Clock, Target } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './Progress.css';

const Progress = () => {
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState('');
    const [progress, setProgress] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadCourses();
    }, []);

    const loadCourses = async () => {
        try {
            const res = await getCourses();
            setCourses(res.data);
            if (res.data.length > 0) {
                setSelectedCourse(res.data[0].id);
                loadProgress(res.data[0].id);
            }
        } catch (error) {
            console.error('Error loading courses:', error);
        }
    };

    const loadProgress = async (courseId) => {
        setLoading(true);
        try {
            const res = await getProgress(courseId);
            setProgress(res.data);
        } catch (error) {
            console.error('Error loading progress:', error);
            setProgress(null);
        } finally {
            setLoading(false);
        }
    };

    const handleCourseChange = (e) => {
        const courseId = e.target.value;
        setSelectedCourse(courseId);
        loadProgress(courseId);
    };

    const getMasteryData = () => {
        if (!progress || !progress.topicMastery) return [];

        return Object.entries(progress.topicMastery).map(([topic, mastery]) => ({
            topic: topic.length > 20 ? topic.substring(0, 20) + '...' : topic,
            mastery: (mastery * 100).toFixed(0)
        }));
    };

    return (
        <div className="progress-page">
            <Navbar />
            <div className="container">
                <div className="page-header">
                    <div>
                        <h1><TrendingUp size={32} /> Progress Tracking</h1>
                        <p>Monitor your learning progress and mastery levels</p>
                    </div>
                    <select value={selectedCourse} onChange={handleCourseChange} className="input" style={{ width: 'auto' }}>
                        {courses.map(course => (
                            <option key={course.id} value={course.id}>{course.title}</option>
                        ))}
                    </select>
                </div>

                {loading ? (
                    <div className="loading">Loading progress...</div>
                ) : !progress || !progress.analytics ? (
                    <div className="empty-state card">
                        <TrendingUp size={64} color="var(--color-gray-400)" />
                        <h3>No Progress Data</h3>
                        <p>Start taking quizzes and logging study sessions to see your progress</p>
                    </div>
                ) : (
                    <>
                        <div className="stats-grid">
                            <div className="stat-card">
                                <div className="stat-icon" style={{ background: 'var(--color-green-100)', color: 'var(--color-green-600)' }}>
                                    <Award size={28} />
                                </div>
                                <div className="stat-content">
                                    <div className="stat-value">{(progress.analytics.overall_mastery * 100).toFixed(0)}%</div>
                                    <div className="stat-label">Overall Mastery</div>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-icon" style={{ background: 'var(--color-orange-100)', color: 'var(--color-orange-600)' }}>
                                    <Target size={28} />
                                </div>
                                <div className="stat-content">
                                    <div className="stat-value">{progress.analytics.average_quiz_score.toFixed(0)}%</div>
                                    <div className="stat-label">Avg Quiz Score</div>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-icon" style={{ background: 'var(--color-gray-200)', color: 'var(--color-gray-700)' }}>
                                    <Clock size={28} />
                                </div>
                                <div className="stat-content">
                                    <div className="stat-value">{progress.analytics.total_study_hours}h</div>
                                    <div className="stat-label">Study Hours</div>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-icon" style={{ background: 'var(--color-orange-100)', color: 'var(--color-orange-600)' }}>
                                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M9 11l3 3L22 4" />
                                        <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
                                    </svg>
                                </div>
                                <div className="stat-content">
                                    <div className="stat-value">{progress.analytics.total_quizzes}</div>
                                    <div className="stat-label">Quizzes Taken</div>
                                </div>
                            </div>
                        </div>

                        {getMasteryData().length > 0 && (
                            <div className="chart-section card">
                                <h2>Topic Mastery</h2>
                                <ResponsiveContainer width="100%" height={300}>
                                    <BarChart data={getMasteryData()}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="topic" />
                                        <YAxis />
                                        <Tooltip />
                                        <Bar dataKey="mastery" fill="var(--color-orange-500)" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        )}

                        <div className="topics-grid">
                            {progress.analytics.weak_topics && progress.analytics.weak_topics.length > 0 && (
                                <div className="topics-card card">
                                    <h3>Topics to Review</h3>
                                    <div className="topics-list">
                                        {progress.analytics.weak_topics.map((item, idx) => (
                                            <div key={idx} className="topic-item weak">
                                                <span className="topic-name">{item.topic}</span>
                                                <span className="topic-score">{(item.mastery * 100).toFixed(0)}%</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {progress.analytics.strong_topics && progress.analytics.strong_topics.length > 0 && (
                                <div className="topics-card card">
                                    <h3>Strong Topics</h3>
                                    <div className="topics-list">
                                        {progress.analytics.strong_topics.map((item, idx) => (
                                            <div key={idx} className="topic-item strong">
                                                <span className="topic-name">{item.topic}</span>
                                                <span className="topic-score">{(item.mastery * 100).toFixed(0)}%</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default Progress;
