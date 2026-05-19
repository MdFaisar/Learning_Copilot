import React, { useState, useEffect, useRef } from 'react';
import Navbar from '../components/layout/Navbar';
import { getCourses, askQuestion, getQAHistory, deleteQAHistory } from '../services/api';
import {
    MessageSquare,
    Send,
    Eraser,
    User,
    Bot,
    ChevronDown,
    Paperclip,
    Search,
    Square
} from 'lucide-react';
import './QA.css';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import ReactMarkdown from 'react-markdown';

// Helper component for typing effect
const Typewriter = ({ text, onComplete, onTick, stopped }) => {
    const [displayedText, setDisplayedText] = useState('');
    const index = useRef(0);
    const intervalRef = useRef(null);

    useEffect(() => {
        // If stopped, clear interval and don't start new one
        if (stopped) {
            if (intervalRef.current) clearInterval(intervalRef.current);
            return;
        }

        index.current = 0;
        setDisplayedText('');

        intervalRef.current = setInterval(() => {
            if (index.current < text.length) {
                setDisplayedText((prev) => text.slice(0, index.current + 1));
                index.current++;
                if (onTick) onTick();
            } else {
                clearInterval(intervalRef.current);
                if (onComplete) onComplete();
            }
        }, 15); // Adjust speed here (lower = faster)

        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, [text, stopped]); // Re-run if text changes, but check stopped in effect

    return (
        <div className="markdown-content">
            <ReactMarkdown>{displayedText}</ReactMarkdown>
        </div>
    );
};

const QA = () => {
    const { user } = useAuth();
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState('');
    const [selectedCourseName, setSelectedCourseName] = useState('');
    const [question, setQuestion] = useState('');
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false); // Track total generation process
    const messagesEndRef = useRef(null);
    const textareaRef = useRef(null);
    const abortControllerRef = useRef(null); // To cancel API requests
    const toast = useToast();

    useEffect(() => {
        loadCourses();
        return () => {
            // Cleanup: abort any pending requests on unmount
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, []);

    const loadCourses = async () => {
        try {
            const res = await getCourses();
            setCourses(res.data);
            if (res.data.length > 0) {
                // Default to first course
                selectCourse(res.data[0]);
            }
        } catch (error) {
            console.error('Error loading courses:', error);
        }
    };

    const selectCourse = (course) => {
        setSelectedCourse(course.id);
        setSelectedCourseName(course.title);
        loadHistory(course.id);
        // Focus textarea after switch
        setTimeout(() => textareaRef.current?.focus(), 100);
    };

    const loadHistory = async (courseId) => {
        try {
            setLoading(true);
            const res = await getQAHistory(courseId);
            // Backend returns Newest First (Desc), we want Oldest First (Asc) for chat log
            setHistory(res.data.reverse());
        } catch (error) {
            setHistory([]);
        } finally {
            setLoading(false);
        }
    };

    const handleStop = () => {
        // 1. Abort network request if active
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
        }

        // 2. Update history to mark the latest message as stopped/not animating
        setHistory(prev => {
            const newHistory = [...prev];
            const lastIdx = newHistory.length - 1;
            if (lastIdx >= 0) {
                // If it was loading (network phase), mark as interrupted
                if (newHistory[lastIdx].loading) {
                    newHistory[lastIdx] = {
                        ...newHistory[lastIdx],
                        loading: false,
                        answer: 'Generation stopped.',
                        animate: false // No animation, static text
                    };
                }
                // If it was animating (typing phase), mark as stopped to freeze Typewriter
                else if (newHistory[lastIdx].animate) {
                    newHistory[lastIdx] = {
                        ...newHistory[lastIdx],
                        stopped: true // Signal Typewriter to stop
                    };
                }
            }
            return newHistory;
        });

        setIsGenerating(false);
    };

    const handleSubmit = async (e) => {
        e?.preventDefault();
        if ((!question.trim() && !e?.isSuggestion) || !selectedCourse) return;

        // Use passed question (from suggestion) or state
        const currentQuestion = e?.isSuggestion ? e.question : question;

        // Cancel previous request if any
        if (abortControllerRef.current) abortControllerRef.current.abort();

        // Create new AbortController
        abortControllerRef.current = new AbortController();

        setQuestion('');
        setIsGenerating(true);
        setHistory(prev => [...prev, { question: currentQuestion, answer: '', loading: true }]);

        // Reset height
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }

        try {
            const res = await askQuestion({
                courseId: selectedCourse,
                question: currentQuestion
            }); // Note: we can't easily pass signal to axios instance without touching api.js, so we rely on manual check mostly.

            if (!abortControllerRef.current) return; // effectively cancelled

            // Replace the loading message with actual response
            setHistory(prev => {
                const newHistory = [...prev];
                // Mark this message for animation
                newHistory[newHistory.length - 1] = { ...res.data, animate: true };
                return newHistory;
            });
        } catch (error) {
            if (abortControllerRef.current === null) {
                // Manually aborted
                console.log('Request aborted manually');
            } else {
                console.error('Error asking question:', error);
                const errorMessage = error.response?.data?.error || 'Failed to get answer.';
                setHistory(prev => {
                    const newHistory = [...prev];
                    newHistory[newHistory.length - 1] = {
                        question: currentQuestion,
                        answer: `Error: ${errorMessage}`,
                        error: true
                    };
                    return newHistory;
                });
            }
            setIsGenerating(false);
        } finally {
            abortControllerRef.current = null;
        }
    };

    const handleAnimationComplete = (index) => {
        setHistory(prev => {
            const newHistory = [...prev];
            if (newHistory[index]) {
                newHistory[index] = { ...newHistory[index], animate: false };
            }
            return newHistory;
        });
        setIsGenerating(false);
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const handleInput = (e) => {
        setQuestion(e.target.value);
        // Auto-resize
        e.target.style.height = 'auto';
        e.target.style.height = `${e.target.scrollHeight}px`;
    };

    // Helper to handle partial submit from suggestions
    const submitSuggestion = (q) => {
        setQuestion(q);
        handleSubmit({ preventDefault: () => { }, isSuggestion: true, question: q });
    };

    // Scroll to bottom effect
    useEffect(() => {
        scrollToBottom();
    }, [history]);

    return (
        <div className="qa-page">
            <Navbar />
            <div className="qa-layout">
                {/* Sidebar */}
                <div className="qa-sidebar">
                    <div className="sidebar-header">
                        <button className="new-chat-btn" onClick={async () => {
                            if (!selectedCourse) return;
                            const ok = window.confirm('Clear all chat history for this course? This cannot be undone.');
                            if (!ok) return;
                            try {
                                const res = await deleteQAHistory(selectedCourse);
                                console.log('Clear history response:', res.data);
                                setHistory([]); // Clear UI history
                                setQuestion('');
                                textareaRef.current?.focus();
                            } catch (err) {
                                console.error('Failed to clear chat history', err);
                                const errMsg = err.response?.data?.error || err.message || 'Failed to clear chat history.';
                                toast.error(`Failed to clear chat history: ${errMsg}`);
                            }
                        }}>
                            <div style={{ background: 'white', border: '1px solid #ddd', borderRadius: '4px', padding: '2px' }}>
                                <Eraser size={14} color="#333" />
                            </div>
                            <span>Clear chat</span>
                        </button>
                    </div>

                    <div className="sidebar-section-label">Your Courses</div>
                    <div className="course-list">
                        {courses.map(course => (
                            <div
                                key={course.id}
                                className={`course-item ${selectedCourse === course.id ? 'active' : ''}`}
                                onClick={() => selectCourse(course)}
                            >
                                <MessageSquare size={16} className="course-icon" />
                                <span>{course.title}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Main Chat Area */}
                <div className="qa-main">
                    {/* Top Bar */}
                    <div className="chat-top-bar">
                        <div className="model-selector">
                            <span>{selectedCourseName || 'Select a Course'}</span>
                            <ChevronDown size={16} style={{ opacity: 0.5 }} />
                        </div>
                        {/* Right side icons could go here */}
                    </div>

                    {/* Chat Content */}
                    <div className="chat-scroll-area">
                        {history.length === 0 ? (
                            <div className="empty-state-container">
                                <div className="has-logo">
                                    <Bot size={48} color="#10a37f" />
                                </div>
                                <h2 className="empty-title">How can I help you?</h2>
                                <div className="suggestions-grid">
                                    <div className="suggestion-card" onClick={() => submitSuggestion("Summarize this course")}>
                                        <div className="suggestion-title">Summarize course</div>
                                        <div className="suggestion-text">Get a quick overview</div>
                                    </div>
                                    <div className="suggestion-card" onClick={() => submitSuggestion("What are the key topics?")}>
                                        <div className="suggestion-title">Key topics</div>
                                        <div className="suggestion-text">List main concepts</div>
                                    </div>
                                    <div className="suggestion-card" onClick={() => submitSuggestion("Create a quiz for me")}>
                                        <div className="suggestion-title">Create quiz</div>
                                        <div className="suggestion-text">Test your knowledge</div>
                                    </div>
                                    <div className="suggestion-card" onClick={() => submitSuggestion("Explain the hardest concept")}>
                                        <div className="suggestion-title">Explain concepts</div>
                                        <div className="suggestion-text">Simplify complex topics</div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="messages-container">
                                {history.map((item, idx) => (
                                    <React.Fragment key={idx}>
                                        {/* User Message */}
                                        <div className="message-row user">
                                            <div className="message-content-wrapper">
                                                <div className="message-avatar avatar-icon-user">
                                                    {user?.photoURL ? (
                                                        <img src={user.photoURL} className="avatar-img" alt="User" />
                                                    ) : (
                                                        <User size={20} />
                                                    )}
                                                </div>
                                                <div className="message-text">
                                                    <div style={{ fontWeight: 600, marginBottom: '4px' }}>You</div>
                                                    <div>{item.question}</div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Assistant Message */}
                                        <div className="message-row assistant">
                                            <div className="message-content-wrapper">
                                                <div className="message-avatar avatar-icon-assistant">
                                                    <Bot size={24} />
                                                </div>
                                                <div className="message-text">
                                                    <div style={{ fontWeight: 600, marginBottom: '4px' }}>Learning Copilot</div>
                                                    {item.loading ? (
                                                        <div className="typing-indicator">Thinking...</div>
                                                    ) : (
                                                        <>
                                                            {item.animate ? (
                                                                <Typewriter
                                                                    text={item.answer || ''}
                                                                    onComplete={() => handleAnimationComplete(idx)}
                                                                    onTick={scrollToBottom}
                                                                    stopped={item.stopped}
                                                                />
                                                            ) : (
                                                                <div className="markdown-content">
                                                                    <ReactMarkdown>{item.answer || ''}</ReactMarkdown>
                                                                </div>
                                                            )}

                                                            {item.citations && item.citations.length > 0 && (
                                                                <div className="citation-box">
                                                                    {item.citations.map((cit, cidx) => (
                                                                        <span key={cidx} title={cit.source}>
                                                                            📚 {cit.source} (p.{cit.page})
                                                                        </span>
                                                                    ))}
                                                                </div>
                                                            )}
                                                        </>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </React.Fragment>
                                ))}
                                <div ref={messagesEndRef} />
                            </div>
                        )}
                    </div>

                    {/* Input Area */}
                    <div className="input-area-wrapper">
                        <div className="input-container">
                            <form className="input-box" onSubmit={handleSubmit}>
                                <div className="attach-btn">
                                    <Paperclip size={20} />
                                </div>
                                <textarea
                                    ref={textareaRef}
                                    className="chat-textarea"
                                    placeholder={`Message ${selectedCourseName || '...'}`}
                                    rows={1}
                                    value={question}
                                    onChange={handleInput}
                                    onKeyDown={handleKeyDown}
                                    disabled={loading}
                                />
                                {isGenerating ? (
                                    <button type="button" className="send-btn stop-btn" onClick={handleStop} title="Stop generating">
                                        <Square size={16} fill="currentColor" />
                                    </button>
                                ) : (
                                    <button type="submit" className="send-btn" disabled={!question.trim() || loading}>
                                        <Send size={16} />
                                    </button>
                                )}
                            </form>
                            <div className="disclaimer">
                                Learning Copilot can make mistakes. Consider checking important information.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default QA;
