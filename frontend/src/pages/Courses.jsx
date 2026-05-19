import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';
import { getCourses, deleteCourse } from '../services/api';
import { Plus, Trash2, Eye } from 'lucide-react';
import './Courses.css';

import { useToast } from '../contexts/ToastContext';

const Courses = () => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const toast = useToast();

    useEffect(() => {
        loadCourses();
    }, []);

    const loadCourses = async () => {
        try {
            const res = await getCourses();
            setCourses(res.data);
        } catch (error) {
            console.error('Error loading courses:', error);
            toast.error('Failed to load courses');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this course?')) return;

        try {
            await deleteCourse(id);
            setCourses(courses.filter(c => c.id !== id));
            toast.success('Course deleted successfully');
        } catch (error) {
            console.error('Error deleting course:', error);
            toast.error('Failed to delete course');
        }
    };

    return (
        <div className="courses-page">
            <Navbar />
            <div className="container">
                <div className="page-header">
                    <div>
                        <h1>My Courses</h1>
                        <p>Manage your courses and study materials</p>
                    </div>
                    <Link to="/courses/new" className="btn btn-primary">
                        <Plus size={20} />
                        Add Course
                    </Link>
                </div>

                {loading ? (
                    <div className="loading">Loading courses...</div>
                ) : courses.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">📚</div>
                        <h3>No courses yet</h3>
                        <p>Create your first course to get started</p>
                        <Link to="/courses/new" className="btn btn-primary">
                            <Plus size={20} />
                            Create Course
                        </Link>
                    </div>
                ) : (
                    <div className="courses-grid">
                        {courses.map((course) => (
                            <div key={course.id} className="course-card">
                                <div className="course-header">
                                    <div className="course-icon">📖</div>
                                    <div className="course-actions">
                                        <button onClick={() => navigate(`/courses/${course.id}`)} className="icon-btn" title="View">
                                            <Eye size={18} />
                                        </button>
                                        <button onClick={() => handleDelete(course.id)} className="icon-btn danger" title="Delete">
                                            <Trash2 size={18} />
                                        </button>
                                    </div>
                                </div>
                                <h3>{course.title}</h3>
                                <p>{course.description || 'No description'}</p>
                                <div className="course-footer">
                                    <span className="badge badge-gray">{course.materials?.length || 0} materials</span>
                                    <Link to={`/courses/${course.id}`} className="view-link">View Details →</Link>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Courses;
