import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { BotMessageSquare, MessageSquare, SendHorizontal, X } from 'lucide-react';
import { getSessionId } from '../utils/session';

export default function ChatWindow() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState([
    { sender: 'ai', text: 'Backend is connected. Ask me about the PDF!' }
  ]);
  
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput || isTyping) return;

    // 1. Add User Message safely
    const userMsg = { sender: 'user', text: trimmedInput };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      console.log("Sending to Backend:", trimmedInput);
      
      const response = await axios.post(
        'http://localhost:8000/chat/',
        { question: trimmedInput },
        { headers: { 'X-Session-Id': getSessionId() } },
      );

      console.log("Backend Raw Response:", response.data);

      // 2. Extract answer safely. Handle both string and object responses.
      let aiText = "I couldn't process that.";
      
      if (response.data && typeof response.data.answer === 'string') {
        aiText = response.data.answer;
      } else if (response.data && typeof response.data === 'string') {
        aiText = response.data;
      }

      setMessages(prev => [...prev, { sender: 'ai', text: aiText }]);

    } catch (error) {
      console.error("FULL CHAT ERROR:", error);
      setMessages(prev => [...prev, { 
        sender: 'ai', 
        text: "Connection Error. Check if Backend is running on Port 8000." 
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  if (!isOpen) {
    return (
      <button onClick={() => setIsOpen(true)} className="chat-launcher">
        <MessageSquare size={24} />
      </button>
    );
  }

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="chat-title">
          <BotMessageSquare size={20} />
          <span>LexGuard AI</span>
        </div>
        <button onClick={() => setIsOpen(false)} className="chat-close">
          <X size={18} />
        </button>
      </div>

      <div ref={scrollRef} className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-row ${msg.sender === 'user' ? 'chat-row-user' : ''}`}>
            <div
              className={`chat-bubble ${
                msg.sender === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {isTyping && <div className="chat-typing">AI is thinking...</div>}
      </div>

      <div className="chat-input-bar">
        <div className="chat-input-row">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            className="chat-input"
          />
          <button onClick={handleSend} className="chat-send">
            <SendHorizontal size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
