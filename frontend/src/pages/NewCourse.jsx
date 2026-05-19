import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';
import { createCourse, getCourses } from '../services/api';
import { ArrowLeft } from 'lucide-react';
import './NewCourse.css';

import { useToast } from '../contexts/ToastContext';

const NewCourse = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        syllabus: ''
    });
    const [loading, setLoading] = useState(false);
    const toast = useToast();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const res = await createCourse(formData);

            // Check for successful response
            if (res.status === 201 && res.data?.id) {
                const courseId = res.data.id;
                toast.success('Course created successfully!');
                navigate(`/courses/${courseId}`);
            } else {
                const msg = res?.data?.error || 'Failed to create course';
                toast.error(msg);
            }
        } catch (error) {
            console.error('Error creating course:', error);
            const errorMsg = error.response?.data?.error || error.message || 'Failed to create course';
            toast.error(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="new-course-page">
            <Navbar />
            <div className="container">
                <button onClick={() => navigate('/courses')} className="back-btn">
                    <ArrowLeft size={20} />
                    Back to Courses
                </button>

                <div className="form-container">
                    <h1>Create New Course</h1>
                    <p>Add a new course to start your learning journey</p>

                    <form onSubmit={handleSubmit} className="course-form">
                        <div className="form-group">
                            <label>Course Title *</label>
                            <input
                                type="text"
                                className="input"
                                value={formData.title}
                                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                required
                                placeholder="e.g., Data Structures and Algorithms"
                            />
                        </div>

                        <div className="form-group">
                            <label>Description</label>
                            <textarea
                                className="textarea"
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                placeholder="Brief description of the course"
                            />
                        </div>

                        <div className="form-group">
                            <label>Syllabus</label>
                            <textarea
                                className="textarea"
                                style={{ minHeight: '200px' }}
                                value={formData.syllabus}
                                onChange={(e) => setFormData({ ...formData, syllabus: e.target.value })}
                                placeholder="Paste your course syllabus here..."
                            />
                        </div>

                        <div className="form-actions">
                            <button type="button" onClick={() => navigate('/courses')} className="btn btn-secondary">
                                Cancel
                            </button>
                            <button type="submit" className="btn btn-primary" disabled={loading}>
                                {loading ? 'Creating...' : 'Create Course'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default NewCourse;
