import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { BookOpen, LayoutDashboard, Calendar, FileQuestion, TrendingUp, LogOut, User, MessageSquare, Code } from 'lucide-react';
import './Navbar.css';

const Navbar = () => {
    const { user, signOut } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();

    const handleSignOut = async () => {
        try {
            await signOut();
            navigate('/');
        } catch (error) {
            console.error('Error signing out:', error);
        }
    };

    const navItems = [
        { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/courses', icon: BookOpen, label: 'Courses' },
        { path: '/study-plan', icon: Calendar, label: 'Study Plan' },
        { path: '/code-editor', icon: Code, label: 'Code Editor' },
        { path: '/qa', icon: MessageSquare, label: 'Q&A' },
        { path: '/quiz', icon: FileQuestion, label: 'Quiz' },
        { path: '/progress', icon: TrendingUp, label: 'Progress' },
    ];

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/dashboard" className="navbar-logo">
                    <span className="logo-icon">📚</span>
                    <span className="logo-text">Learning Copilot</span>
                </Link>

                <div className="navbar-links">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;

                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`nav-link ${isActive ? 'active' : ''}`}
                            >
                                <Icon size={18} />
                                <span>{item.label}</span>
                            </Link>
                        );
                    })}
                </div>

                <div className="navbar-user">
                    <div className="user-info">
                        {user?.photoURL ? (
                            <img src={user.photoURL} alt={user.displayName} className="user-avatar" />
                        ) : (
                            <div className="user-avatar-placeholder">
                                <User size={20} />
                            </div>
                        )}
                        <span className="user-name">{user?.displayName || 'User'}</span>
                    </div>
                    <button onClick={handleSignOut} className="btn-logout">
                        <LogOut size={18} />
                        <span>Logout</span>
                    </button>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
