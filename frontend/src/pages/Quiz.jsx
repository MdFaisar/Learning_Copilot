import React, { useState, useEffect } from 'react';
import Navbar from '../components/layout/Navbar';
import { getCourses, generateQuiz, submitQuiz } from '../services/api';
import { FileQuestion, CheckCircle, XCircle } from 'lucide-react';
import './Quiz.css';

import { useToast } from '../contexts/ToastContext';

const Quiz = () => {
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState('');
    const [quiz, setQuiz] = useState(null);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const toast = useToast();

    useEffect(() => {
        loadCourses();
    }, []);

    const loadCourses = async () => {
        try {
            const res = await getCourses();
            setCourses(res.data);
            if (res.data.length > 0) {
                setSelectedCourse(res.data[0].id);
            }
        } catch (error) {
            console.error('Error loading courses:', error);
        }
    };

    const handleGenerateQuiz = async () => {
        if (!selectedCourse) return;

        setLoading(true);
        setQuiz(null);
        setResults(null);

        try {
            const res = await generateQuiz({
                courseId: selectedCourse,
                topics: [],
                numQuestions: 5
            });
            setQuiz(res.data);
        } catch (error) {
            console.error('Error generating quiz:', error);
            const errMsg = error.response?.data?.error || error.message || 'Failed to generate quiz';
            toast.error(`Failed to generate quiz: ${errMsg}`);
        } finally {
            setLoading(false);
        }
    };

    const handleAnswerSelect = (questionIdx, answer) => {
        const updatedQuiz = { ...quiz };
        updatedQuiz.questions[questionIdx].userAnswer = answer;
        setQuiz(updatedQuiz);
    };

    const handleSubmit = async () => {
        try {
            const res = await submitQuiz({
                quizId: quiz.id,
                courseId: selectedCourse,
                questions: quiz.questions
            });
            setResults(res.data.results);
            // Store the questions with correctAnswer for display in results
            if (res.data.questions) {
                setQuiz(prev => ({
                    ...prev,
                    questions: res.data.questions
                }));
            }
        } catch (error) {
            console.error('Error submitting quiz:', error);
            const errMsg = error.response?.data?.error || error.message || 'Failed to submit quiz';
            toast.error(errMsg);
        }
    };

    const handleNextQuiz = () => {
        setResults(null);
        setQuiz(null);
        handleGenerateQuiz();
    };

    return (
        <div className="quiz-page">
            <Navbar />
            <div className="container">
                <div className="page-header">
                    <div>
                        <h1><FileQuestion size={32} /> Quiz</h1>
                        <p>Test your knowledge with adaptive quizzes</p>
                    </div>
                </div>

                <div className="quiz-controls card">
                    <select value={selectedCourse} onChange={(e) => setSelectedCourse(e.target.value)} className="input">
                        <option value="">Select a course</option>
                        {courses.map(course => (
                            <option key={course.id} value={course.id}>{course.title}</option>
                        ))}
                    </select>
                    <button onClick={handleGenerateQuiz} className="btn btn-primary" disabled={!selectedCourse || loading}>
                        {loading ? 'Generating...' : 'Generate Quiz'}
                    </button>
                </div>

                {results ? (
                    <div className="results-section">
                        <div className="results-header card">
                            <h2>Quiz Results</h2>
                            <div className="score-display">
                                <div className="score-circle">
                                    <span className="score-value">{results.score.toFixed(0)}%</span>
                                </div>
                                <div className="score-details">
                                    <p>{results.correct} out of {results.total} correct</p>
                                </div>
                            </div>
                            <button onClick={handleNextQuiz} className="btn btn-primary btn-next-quiz">
                                Take Another Quiz
                            </button>
                        </div>

                        <div className="questions-review">
                            {quiz.questions.map((q, idx) => (
                                <div key={idx} className={`question-card card ${q.userAnswer === q.correctAnswer ? 'correct' : 'incorrect'}`}>
                                    <div className="question-header">
                                        <span className="question-number">Question {idx + 1}</span>
                                        {q.userAnswer === q.correctAnswer ? (
                                            <CheckCircle size={24} color="#10B981" />
                                        ) : (
                                            <XCircle size={24} color="#EF4444" />
                                        )}
                                    </div>
                                    <p className="question-text">{q.question}</p>
                                    <div className="answer-review">
                                        <p><strong>Your answer:</strong> {q.userAnswer || 'Not answered'}</p>
                                        <p><strong>Correct answer:</strong> {q.correctAnswer}</p>
                                        {q.explanation && <p className="explanation"><strong>Explanation:</strong> {q.explanation}</p>}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : quiz ? (
                    <div className="quiz-section">
                        {quiz.questions.map((q, idx) => (
                            <div key={idx} className="question-card card">
                                <div className="question-header">
                                    <span className="question-number">Question {idx + 1}</span>
                                    <span className="badge badge-gray">{q.topic}</span>
                                </div>
                                <p className="question-text">{q.question}</p>
                                <div className="options-list">
                                    {q.options.map((option, optIdx) => (
                                        <label key={optIdx} className={`option-item ${q.userAnswer === option ? 'selected' : ''}`}>
                                            <input
                                                type="radio"
                                                name={`question-${idx}`}
                                                checked={q.userAnswer === option}
                                                onChange={() => handleAnswerSelect(idx, option)}
                                            />
                                            <span>{option}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        ))}

                        <button onClick={handleSubmit} className="btn btn-success btn-large">
                            Submit Quiz
                        </button>
                    </div>
                ) : (
                    <div className="empty-state card">
                        <FileQuestion size={64} color="var(--color-gray-400)" />
                        <h3>No Quiz Generated</h3>
                        <p>Select a course and generate a quiz to get started</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Quiz;
