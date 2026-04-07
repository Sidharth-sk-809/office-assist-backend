import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader } from 'lucide-react';
import { sendChatMessage } from '../services/api';
import './Chat.css';

function Chat({ user }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hello ${user.name}! 👋 I'm your HR assistant. Ask me anything about company policies, benefits, leave policies, or any other HR-related questions!`,
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await sendChatMessage(userMessage, user.conversationId);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '❌ Sorry, I encountered an error. Please make sure the backend is running and try again.',
          error: true,
        },
      ]);
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  const suggestedQuestions = [
    'What is the vacation policy?',
    'How do I apply for leave?',
    'What are the working hours?',
    'Tell me about health benefits',
  ];

  return (
    <div className="chat-page">
      <div className="container">
        <div className="chat-container card">
          <div className="chat-header">
            <h2>💬 Policy Chat Assistant</h2>
            <p>Ask me anything about company policies</p>
          </div>

          <div className="messages-container">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message ${message.role} ${message.error ? 'error' : ''}`}
              >
                <div className="message-icon">
                  {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                </div>
                <div className="message-content">
                  <p>{message.content}</p>
                  {message.sources && message.sources.length > 0 && (
                    <div className="sources">
                      <strong>Sources:</strong>
                      <ul>
                        {message.sources.map((source, idx) => (
                          <li key={idx}>
                            {source.title || source.uri}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="message assistant loading">
                <div className="message-icon">
                  <Bot size={20} />
                </div>
                <div className="message-content">
                  <Loader className="spinner-icon" />
                  <span>Thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {messages.length === 1 && (
            <div className="suggested-questions">
              <p className="suggested-label">Try asking:</p>
              <div className="suggestions-grid">
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    className="suggestion-btn"
                    onClick={() => setInput(question)}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="chat-input-form">
            <input
              type="text"
              className="input chat-input"
              placeholder="Type your question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <button type="submit" className="btn btn-primary" disabled={loading || !input.trim()}>
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Chat;
