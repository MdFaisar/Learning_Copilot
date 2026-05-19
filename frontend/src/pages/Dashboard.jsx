import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';
import { getCourses, getProgress } from '../services/api';
import { BookOpen, Calendar, TrendingUp, Plus, ArrowRight, Code } from 'lucide-react';
import './Dashboard.css';

const Dashboard = () => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        totalCourses: 0,
        avgMastery: 0,
        totalStudyHours: 0,
        quizzesCompleted: 0
    });

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            const coursesRes = await getCourses();
            setCourses(coursesRes.data || []);

            // Load progress for all courses in parallel with timeout
            const progressPromises = (coursesRes.data || []).map(course =>
                getProgress(course.id).catch(err => {
                    console.log('No progress for course:', course.id);
                    return null;
                })
            );

            const progressResults = await Promise.all(progressPromises);

            // Calculate stats from progress data
            let totalMastery = 0;
            let totalHours = 0;
            let totalQuizzes = 0;
            let coursesWithProgress = 0;

            progressResults.forEach(progressRes => {
                if (progressRes?.data?.analytics) {
                    const analytics = progressRes.data.analytics;
                    totalMastery += analytics.overall_mastery || 0;
                    totalHours += analytics.total_study_hours || 0;
                    totalQuizzes += analytics.total_quizzes || 0;
                    coursesWithProgress++;
                }
            });

            setStats({
                totalCourses: coursesRes.data?.length || 0,
                avgMastery: coursesWithProgress > 0 ? (totalMastery / coursesWithProgress * 100).toFixed(1) : 0,
                totalStudyHours: totalHours.toFixed(1),
                quizzesCompleted: totalQuizzes
            });
        } catch (error) {
            console.error('Error loading dashboard:', error);
            setCourses([]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard-page">
            <Navbar />

            <div className="dashboard-container">
                <div className="dashboard-header">
                    <div>
                        <h1>Dashboard</h1>
                        <p>Welcome back! Here's your learning overview</p>
                    </div>
                    <Link to="/courses/new" className="btn btn-primary">
                        <Plus size={20} />
                        Add Course
                    </Link>
                </div>

                {loading ? (
                    <div className="loading-state">Loading...</div>
                ) : (
                    <>
                        <div className="stats-grid">
                            <div className="stat-card">
                                <div className="stat-icon" style={{ background: 'var(--color-orange-100)', color: 'var(--color-orange-600)' }}>
                                    <BookOpen size={24} />
                                </div>
                                <div className="stat-content">
                                    <div className="stat-value">{stats.totalCourses}</div>
                                    <div className="stat-label">Active Courses</div>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-icon" style={{ background: 'var(--color-green-100)', color: 'var(--color-green-600)' }}>
                                    <TrendingUp size={24} />
                                </div>
                                <div className="stat-content">
                                    <div className="stat-value">{stats.avgMastery}%</div>
                                    <div className="stat-label">Avg Mastery</div>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-icon" style={{ background: 'var(--color-gray-200)', color: 'var(--color-gray-700)' }}>
                                    <Calendar size={24} />
                                </div>
                                <div className="stat-content">
                                    <div className="stat-value">{stats.totalStudyHours}h</div>
                                    <div className="stat-label">Study Hours</div>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-icon" style={{ background: 'var(--color-orange-100)', color: 'var(--color-orange-600)' }}>
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M9 11l3 3L22 4" />
                                        <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
                                    </svg>
                                </div>
                                <div className="stat-content">
                                    <div className="stat-value">{stats.quizzesCompleted}</div>
                                    <div className="stat-label">Quizzes Completed</div>
                                </div>
                            </div>
                        </div>

                        <div className="dashboard-content">
                            <div className="section">
                                <div className="section-header">
                                    <h2>Your Courses</h2>
                                    <Link to="/courses" className="view-all-link">
                                        View All <ArrowRight size={16} />
                                    </Link>
                                </div>

                                {courses.length === 0 ? (
                                    <div className="empty-state">
                                        <div className="empty-icon">📚</div>
                                        <h3>No courses yet</h3>
                                        <p>Get started by adding your first course</p>
                                        <Link to="/courses/new" className="btn btn-primary">
                                            <Plus size={20} />
                                            Add Your First Course
                                        </Link>
                                    </div>
                                ) : (
                                    <div className="courses-grid">
                                        {courses.slice(0, 4).map((course) => (
                                            <Link key={course.id} to={`/courses/${course.id}`} className="course-card">
                                                <div className="course-icon">📖</div>
                                                <h3>{course.title}</h3>
                                                <p>{course.description || 'No description'}</p>
                                                <div className="course-meta">
                                                    <span className="badge badge-gray">
                                                        {course.materials?.length || 0} materials
                                                    </span>
                                                </div>
                                            </Link>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <div className="quick-actions">
                                <h2>Quick Actions</h2>
                                <div className="actions-grid">
                                    <Link to="/study-plan" className="action-card">
                                        <Calendar size={32} />
                                        <h3>Study Plan</h3>
                                        <p>View your personalized study roadmap</p>
                                    </Link>
                                    <Link to="/quiz" className="action-card">
                                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                            <path d="M9 11l3 3L22 4" />
                                            <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
                                        </svg>
                                        <h3>Take Quiz</h3>
                                        <p>Test your knowledge with adaptive quizzes</p>
                                    </Link>
                                    <Link to="/progress" className="action-card">
                                        <TrendingUp size={32} />
                                        <h3>Progress</h3>
                                        <p>Track your mastery and improvements</p>
                                    </Link>
                                    <Link to="/code-editor" className="action-card">
                                        <Code size={32} />
                                        <h3>Code Editor</h3>
                                        <p>Practice coding with AI assistance</p>
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default Dashboard;
