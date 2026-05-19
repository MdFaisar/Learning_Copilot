import React, { useState, useEffect } from 'react';
import Navbar from '../components/layout/Navbar';
import { getCourses, getStudyPlan, updateStudyPlan } from '../services/api';
import { Calendar, CheckCircle, Circle } from 'lucide-react';
import './StudyPlan.css';

const StudyPlan = () => {
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState('');
    const [plan, setPlan] = useState(null);
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
                loadPlan(res.data[0].id);
            }
        } catch (error) {
            console.error('Error loading courses:', error);
        }
    };

    const loadPlan = async (courseId) => {
        setLoading(true);
        try {
            const res = await getStudyPlan(courseId);
            setPlan(res.data);
        } catch (error) {
            console.log('No study plan found');
            setPlan(null);
        } finally {
            setLoading(false);
        }
    };

    const handleCourseChange = (e) => {
        const courseId = e.target.value;
        setSelectedCourse(courseId);
        loadPlan(courseId);
    };

    const toggleTask = async (weekIdx, taskIdx) => {
        if (!plan) return;

        const updatedPlan = { ...plan };
        updatedPlan.weeks[weekIdx].tasks[taskIdx].completed = !updatedPlan.weeks[weekIdx].tasks[taskIdx].completed;

        try {
            await updateStudyPlan(plan.id, { weeks: updatedPlan.weeks });
            setPlan(updatedPlan);
        } catch (error) {
            console.error('Error updating plan:', error);
        }
    };

    return (
        <div className="study-plan-page">
            <Navbar />
            <div className="container">
                <div className="page-header">
                    <div>
                        <h1><Calendar size={32} /> Study Plan</h1>
                        <p>Your personalized learning roadmap</p>
                    </div>
                    <select value={selectedCourse} onChange={handleCourseChange} className="input" style={{ width: 'auto' }}>
                        {courses.map(course => (
                            <option key={course.id} value={course.id}>{course.title}</option>
                        ))}
                    </select>
                </div>

                {loading ? (
                    <div className="loading">Loading study plan...</div>
                ) : !plan ? (
                    <div className="empty-state card">
                        <h3>No Study Plan Yet</h3>
                        <p>Generate a study plan from the course detail page</p>
                    </div>
                ) : (
                    <div className="plan-content">
                        <div className="plan-info card">
                            <div className="info-item">
                                <span className="label">Duration:</span>
                                <span className="value">{plan.weeks.length} weeks</span>
                            </div>
                            <div className="info-item">
                                <span className="label">Hours/Week:</span>
                                <span className="value">{plan.constraints.hoursPerWeek}h</span>
                            </div>
                        </div>

                        <div className="weeks-list">
                            {plan.weeks.map((week, weekIdx) => (
                                <div key={weekIdx} className="week-card card">
                                    <div className="week-header">
                                        <h3>Week {week.weekNumber}</h3>
                                        <span className="badge badge-primary">{week.topics.join(', ')}</span>
                                    </div>
                                    <p className="week-goals">{week.goals}</p>
                                    <div className="tasks-list">
                                        {week.tasks.map((task, taskIdx) => (
                                            <div key={taskIdx} className="task-item" onClick={() => toggleTask(weekIdx, taskIdx)}>
                                                {task.completed ? <CheckCircle size={20} color="var(--color-success)" /> : <Circle size={20} />}
                                                <div className="task-content">
                                                    <div className="task-title">{task.title}</div>
                                                    <div className="task-meta">
                                                        <span>{task.estimatedHours}h</span>
                                                        <span>•</span>
                                                        <span>{task.description}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default StudyPlan;
