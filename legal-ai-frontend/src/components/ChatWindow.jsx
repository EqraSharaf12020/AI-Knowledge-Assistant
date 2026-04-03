import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { MessageSquare, X, SendHorizontal, BotMessageSquare, Loader2 } from 'lucide-react';

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
      
      const response = await axios.post('http://localhost:8000/chat/', { 
        question: trimmedInput 
      });

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

  if (!isOpen) return (
    <button onClick={() => setIsOpen(true)} className="fixed bottom-8 right-8 z-50 p-4 bg-blue-600 text-white rounded-full shadow-2xl transition-transform hover:scale-110">
      <MessageSquare size={24} />
    </button>
  );

  return (
    <div className="fixed bottom-8 right-8 z-50 w-96 h-[34rem] bg-white rounded-3xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 bg-slate-900 flex items-center justify-between">
        <div className="flex items-center gap-2">
           <BotMessageSquare size={20} className="text-blue-400" />
           <span className="text-white font-bold text-sm">LexGuard AI</span>
        </div>
        <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-white"><X size={18} /></button>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 p-4 overflow-y-auto bg-slate-50">
        {messages.map((msg, i) => (
          <div key={i} className={`flex mb-4 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-2xl text-sm ${
              msg.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-white text-slate-800 border'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        {isTyping && <div className="text-xs text-slate-400 animate-pulse">AI is thinking...</div>}
      </div>

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input 
            type="text" 
            value={input} 
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            className="flex-1 bg-slate-100 border-none rounded-full px-4 py-2 text-sm outline-none focus:ring-1 focus:ring-blue-400"
          />
          <button onClick={handleSend} className="p-2 bg-blue-600 text-white rounded-full">
            <SendHorizontal size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}