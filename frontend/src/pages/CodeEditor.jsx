import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { Play, Loader, Bug, Lightbulb, TestTube, Sparkles, Code, Terminal } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import {
    getSupportedLanguages,
    executeCode,
    debugCode,
    explainCodeAPI,
    improveCodeAPI,
    generateTestCases
} from '../services/api';
import './CodeEditor.css';

const CodeEditor = () => {
    const navigate = useNavigate();
    const [languages, setLanguages] = useState([]);
    const [selectedLanguage, setSelectedLanguage] = useState('python');
    const [code, setCode] = useState('# Write your code here\nprint("Hello, World!")');
    const [input, setInput] = useState('');
    const [output, setOutput] = useState('');
    const [isRunning, setIsRunning] = useState(false);
    const [executionTime, setExecutionTime] = useState(null);
    const [executionMemory, setExecutionMemory] = useState(null);
    const [aiAnalysis, setAiAnalysis] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [activeTab, setActiveTab] = useState('output');
    const [theme, setTheme] = useState('vs-dark');

    // Code templates for different languages
    const codeTemplates = {
        python: '# Python Code\nprint("Hello, World!")',
        javascript: '// JavaScript Code\nconsole.log("Hello, World!");',
        java: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
        c: '#include <stdio.h>\n\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}',
        cpp: '#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}',
        csharp: 'using System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello, World!");\n    }\n}',
        ruby: '# Ruby Code\nputs "Hello, World!"',
        go: 'package main\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}',
        rust: 'fn main() {\n    println!("Hello, World!");\n}',
        php: '<?php\necho "Hello, World!";\n?>',
        swift: 'import Foundation\nprint("Hello, World!")',
        kotlin: 'fun main() {\n    println("Hello, World!")\n}',
        typescript: '// TypeScript Code\nconsole.log("Hello, World!");',
    };

    // Fallback languages list in case API fails
    const fallbackLanguages = [
        { name: 'Python', value: 'python', id: 71 },
        { name: 'JavaScript', value: 'javascript', id: 63 },
        { name: 'Java', value: 'java', id: 62 },
        { name: 'C', value: 'c', id: 50 },
        { name: 'C++', value: 'cpp', id: 54 },
        { name: 'C#', value: 'csharp', id: 51 },
        { name: 'Ruby', value: 'ruby', id: 72 },
        { name: 'Go', value: 'go', id: 60 },
        { name: 'Rust', value: 'rust', id: 73 },
        { name: 'PHP', value: 'php', id: 68 },
        { name: 'Swift', value: 'swift', id: 83 },
        { name: 'Kotlin', value: 'kotlin', id: 78 },
        { name: 'TypeScript', value: 'typescript', id: 74 },
    ];

    useEffect(() => {
        fetchLanguages();
    }, []);

    const fetchLanguages = async () => {
        try {
            const response = await getSupportedLanguages();
            if (response.data.success) {
                setLanguages(response.data.languages);
            } else {
                setLanguages(fallbackLanguages);
            }
        } catch (error) {
            console.error('Error fetching languages:', error);
            setLanguages(fallbackLanguages);
            setOutput('Note: Using offline language list. Some features may be limited.');
        }
    };

    const handleLanguageChange = (e) => {
        const newLanguage = e.target.value;
        setSelectedLanguage(newLanguage);
        setCode(codeTemplates[newLanguage] || '// Start coding...');
        setOutput('');
        setAiAnalysis('');
    };

    const runCode = async () => {
        setIsRunning(true);
        setOutput('Running code...');
        setExecutionTime(null);
        setExecutionMemory(null);
        setActiveTab('output');

        try {
            const response = await executeCode({
                language: selectedLanguage,
                code: code,
                input: input
            });

            if (response.data.success) {
                const result = response.data.result;
                let outputText = '';

                if (result.stdout) {
                    outputText += `Output:\n${result.stdout}\n`;
                }

                if (result.stderr) {
                    outputText += `\nErrors:\n${result.stderr}\n`;
                }

                if (result.compile_output) {
                    outputText += `\nCompilation Output:\n${result.compile_output}\n`;
                }

                if (result.error) {
                    outputText += `\nError:\n${result.error}\n`;
                }

                outputText += `\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
                outputText += `Status: ${result.status}\n`;
                outputText += `Execution Time: ${result.time || '0'}s\n`;
                outputText += `Memory Used: ${result.memory || '0'} KB`;

                setOutput(outputText || 'No output');
                setExecutionTime(result.time);
                setExecutionMemory(result.memory);

                // Auto-analyze errors
                if (result.error || result.stderr || result.compile_output) {
                    analyzeError(result.error || result.stderr || result.compile_output);
                }
            } else {
                setOutput(`Error: ${response.data.error}`);
            }
        } catch (error) {
            setOutput(`Error: ${error.message}`);
        } finally {
            setIsRunning(false);
        }
    };

    const analyzeError = async (errorMessage) => {
        setIsAnalyzing(true);
        setActiveTab('ai-debug');

        try {
            const response = await debugCode({
                code: code,
                language: selectedLanguage,
                error: errorMessage,
                errorType: 'runtime'
            });

            if (response.data.success) {
                setAiAnalysis(response.data.analysis);
            } else {
                setAiAnalysis(`Error: ${response.data.error}`);
            }
        } catch (error) {
            setAiAnalysis(`Error analyzing code: ${error.message}`);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const explainCode = async () => {
        setIsAnalyzing(true);
        setActiveTab('ai-debug');
        setAiAnalysis('Analyzing your code...');

        try {
            const response = await explainCodeAPI({
                code: code,
                language: selectedLanguage,
                output: output
            });

            if (response.data.success) {
                setAiAnalysis(response.data.explanation);
            } else {
                setAiAnalysis(`Error: ${response.data.error}`);
            }
        } catch (error) {
            setAiAnalysis(`Error explaining code: ${error.message}`);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const improveCode = async () => {
        setIsAnalyzing(true);
        setActiveTab('ai-debug');
        setAiAnalysis('Getting improvement suggestions...');

        try {
            const response = await improveCodeAPI({
                code: code,
                language: selectedLanguage
            });

            if (response.data.success) {
                setAiAnalysis(response.data.suggestions);
            } else {
                setAiAnalysis(`Error: ${response.data.error}`);
            }
        } catch (error) {
            setAiAnalysis(`Error getting suggestions: ${error.message}`);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const generateTests = async () => {
        setIsAnalyzing(true);
        setActiveTab('ai-debug');
        setAiAnalysis('Generating test cases...');

        try {
            const response = await generateTestCases({
                code: code,
                language: selectedLanguage
            });

            if (response.data.success) {
                setAiAnalysis(response.data.test_cases);
            } else {
                setAiAnalysis(`Error: ${response.data.error}`);
            }
        } catch (error) {
            setAiAnalysis(`Error generating tests: ${error.message}`);
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="code-editor-container">
            <div className="code-editor-header">
                <div className="header-left">
                    <Code className="header-icon" />
                    <h1>Code Editor</h1>
                </div>
                <button className="back-btn" onClick={() => navigate('/dashboard')}>
                    ← Back to Dashboard
                </button>
            </div>

            <div className="editor-layout">
                {/* Left Panel - Code Editor */}
                <div className="editor-panel">
                    <div className="editor-controls">
                        <select
                            value={selectedLanguage}
                            onChange={handleLanguageChange}
                            className="language-selector"
                        >
                            {languages.map(lang => (
                                <option key={lang.value} value={lang.value}>
                                    {lang.name}
                                </option>
                            ))}
                        </select>

                        <div className="control-buttons">
                            <button
                                className="theme-toggle"
                                onClick={() => setTheme(theme === 'vs-dark' ? 'light' : 'vs-dark')}
                            >
                                {theme === 'vs-dark' ? '☀️' : '🌙'}
                            </button>
                            <button
                                className="run-btn"
                                onClick={runCode}
                                disabled={isRunning}
                            >
                                {isRunning ? (
                                    <>
                                        <Loader className="spin" size={16} />
                                        Running...
                                    </>
                                ) : (
                                    <>
                                        <Play size={16} />
                                        Run Code
                                    </>
                                )}
                            </button>
                        </div>
                    </div>

                    <div className="monaco-editor-wrapper">
                        <Editor
                            height="calc(100vh - 280px)"
                            language={selectedLanguage === 'cpp' ? 'cpp' : selectedLanguage}
                            value={code}
                            onChange={(value) => setCode(value || '')}
                            theme={theme}
                            options={{
                                minimap: { enabled: true },
                                fontSize: 14,
                                lineNumbers: 'on',
                                roundedSelection: false,
                                scrollBeyondLastLine: false,
                                automaticLayout: true,
                                tabSize: 4,
                            }}
                        />
                    </div>

                    <div className="input-section">
                        <label>
                            <Terminal size={14} />
                            Input (stdin):
                        </label>
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Enter input for your program..."
                            rows={3}
                        />
                    </div>
                </div>

                {/* Right Panel - Output & AI Assistant */}
                <div className="output-panel">
                    <div className="panel-tabs">
                        <button
                            className={`tab ${activeTab === 'output' ? 'active' : ''}`}
                            onClick={() => setActiveTab('output')}
                        >
                            <Terminal size={16} />
                            Output
                        </button>
                        <button
                            className={`tab ${activeTab === 'ai-debug' ? 'active' : ''}`}
                            onClick={() => setActiveTab('ai-debug')}
                        >
                            <Sparkles size={16} />
                            AI Assistant
                        </button>
                    </div>

                    {activeTab === 'output' && (
                        <div className="output-content">
                            <pre>{output || 'Run your code to see output here...'}</pre>
                            {executionTime !== null && (
                                <div className="execution-stats">
                                    <span>⏱️ {executionTime}s</span>
                                    <span>💾 {executionMemory} KB</span>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'ai-debug' && (
                        <div className="ai-content">
                            <div className="ai-actions">
                                <button onClick={explainCode} disabled={isAnalyzing}>
                                    <Lightbulb size={16} />
                                    Explain Code
                                </button>
                                <button onClick={improveCode} disabled={isAnalyzing}>
                                    <Bug size={16} />
                                    Improve Code
                                </button>
                                <button onClick={generateTests} disabled={isAnalyzing}>
                                    <TestTube size={16} />
                                    Generate Tests
                                </button>
                            </div>

                            <div className="ai-output">
                                {isAnalyzing ? (
                                    <div className="analyzing">
                                        <Loader className="spin" size={24} />
                                        <p>AI is analyzing...</p>
                                    </div>
                                ) : aiAnalysis ? (
                                    <ReactMarkdown>{aiAnalysis}</ReactMarkdown>
                                ) : (
                                    <p className="placeholder">
                                        Click a button above to get AI assistance with your code!
                                    </p>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CodeEditor;
