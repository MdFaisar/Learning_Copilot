import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';
import { getCourse, uploadMaterial, processMaterials, generateStudyPlan, askQuestion } from '../services/api';
import { Upload, FileText, MessageSquare, Calendar, ArrowLeft } from 'lucide-react';
import './CourseDetail.css';
import { useToast } from '../contexts/ToastContext';

const CourseDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState(null);
    const [askingQuestion, setAskingQuestion] = useState(false);
    const toast = useToast();

    useEffect(() => {
        loadCourse();
    }, [id]);

    const loadCourse = async () => {
        try {
            const res = await getCourse(id);
            setCourse(res.data);
        } catch (error) {
            console.error('Error loading course:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            await uploadMaterial(id, formData);
            await loadCourse();
            toast.success('Material uploaded successfully!');
        } catch (error) {
            console.error('Error uploading material:', error);
            toast.error('Failed to upload material');
        } finally {
            setUploading(false);
        }
    };

    const handleProcessMaterials = async () => {
        setProcessing(true);
        try {
            await processMaterials(id);
            toast.success('Materials processed successfully! You can now ask questions.');
        } catch (error) {
            console.error('Error processing materials:', error);
            toast.error('Failed to process materials');
        } finally {
            setProcessing(false);
        }
    };

    const handleGenerateStudyPlan = async () => {
        setGenerating(true);
        try {
            await generateStudyPlan({
                courseId: id,
                hoursPerWeek: 10,
                targetWeeks: 12,
                priorities: []
            });
            toast.success('Study plan generated! Check the Study Plan page.');
            navigate('/study-plan');
        } catch (error) {
            console.error('Error generating study plan:', error);
            toast.error('Failed to generate study plan');
        } finally {
            setGenerating(false);
        }
    };

    const handleAskQuestion = async (e) => {
        e.preventDefault();
        if (!question.trim()) return;

        setAskingQuestion(true);
        try {
            const res = await askQuestion({ courseId: id, question });
            setAnswer(res.data);
            setQuestion('');
        } catch (error) {
            console.error('Error asking question:', error);
            toast.error('Failed to get answer. Make sure materials are processed.');
        } finally {
            setAskingQuestion(false);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (!course) return <div>Course not found</div>;

    return (
        <div className="course-detail-page">
            <Navbar />
            <div className="container">
                <button onClick={() => navigate('/courses')} className="back-btn">
                    <ArrowLeft size={20} />
                    Back to Courses
                </button>

                <div className="course-header">
                    <div>
                        <h1>{course.title}</h1>
                        <p>{course.description}</p>
                    </div>
                </div>

                <div className="course-content">
                    <div className="section card">
                        <h2><FileText size={24} /> Course Materials</h2>
                        <div className="materials-list">
                            {course.materials && course.materials.length > 0 ? (
                                course.materials.map((material, idx) => (
                                    <div key={idx} className="material-item">
                                        <FileText size={18} />
                                        <span>{material.name}</span>
                                    </div>
                                ))
                            ) : (
                                <p className="text-muted">No materials uploaded yet</p>
                            )}
                        </div>

                        <div className="upload-section">
                            <label className="btn btn-secondary">
                                <Upload size={18} />
                                {uploading ? 'Uploading...' : 'Upload PDF'}
                                <input type="file" accept=".pdf" onChange={handleFileUpload} style={{ display: 'none' }} disabled={uploading} />
                            </label>

                            {course.materials && course.materials.length > 0 && (
                                <button onClick={handleProcessMaterials} className="btn btn-primary" disabled={processing}>
                                    {processing ? 'Processing...' : 'Process Materials for Q&A'}
                                </button>
                            )}
                        </div>
                    </div>

                    <div className="section card">
                        <h2><Calendar size={24} /> Study Plan</h2>
                        <p>Generate a personalized study plan based on your syllabus and schedule.</p>
                        <button onClick={handleGenerateStudyPlan} className="btn btn-success" disabled={generating}>
                            {generating ? 'Generating...' : 'Generate Study Plan'}
                        </button>
                    </div>

                    <div className="section card">
                        <h2><MessageSquare size={24} /> Ask a Question</h2>
                        <form onSubmit={handleAskQuestion} className="qa-form">
                            <textarea
                                className="textarea"
                                value={question}
                                onChange={(e) => setQuestion(e.target.value)}
                                placeholder="Ask a question about this course..."
                                disabled={askingQuestion}
                            />
                            <button type="submit" className="btn btn-primary" disabled={askingQuestion || !question.trim()}>
                                {askingQuestion ? 'Getting Answer...' : 'Ask Question'}
                            </button>
                        </form>

                        {answer && (
                            <div className="answer-box">
                                <h3>Answer:</h3>
                                <p>{answer.answer}</p>
                                {answer.citations && answer.citations.length > 0 && (
                                    <div className="citations">
                                        <h4>Sources:</h4>
                                        {answer.citations.map((citation, idx) => (
                                            <div key={idx} className="citation">
                                                [{citation.number}] {citation.source} (Page {citation.page})
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CourseDetail;
