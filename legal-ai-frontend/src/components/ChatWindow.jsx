import React, { useState } from 'react';
import { MessageSquare, X, SendHorizontal, BotMessageSquare } from 'lucide-react';

const Message = ({ sender, text }) => (
  <div className={`flex gap-3 mb-4 ${sender === 'user' ? 'justify-end' : ''}`}>
    {sender === 'ai' && (
      <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center border border-slate-200 mt-0.5">
        <BotMessageSquare size={16} className="text-blue-600" />
      </div>
    )}
    <div className={`max-w-[75%] p-3.5 rounded-2xl text-sm ${
      sender === 'ai' 
        ? 'bg-white text-slate-700 rounded-bl-none border border-slate-100' 
        : 'bg-blue-600 text-white rounded-br-none'
    }`}>
      <p className="leading-relaxed">{text}</p>
      {sender === 'ai' && (
        <span className="text-[9px] text-slate-400 mt-2 block italic font-medium">Source: Page 4, Section 6.2</span>
      )}
    </div>
  </div>
);

export default function ChatWindow() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { sender: 'ai', text: 'Hi! I’ve analyzed the contract. What specific clause can I clarify for you?' }
  ]);

  const handleSend = () => {
    if (!input.trim()) return;
    const userMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = { 
        sender: 'ai', 
        text: 'The non-compete clause seems quite aggressive. It restricts you for 3 years, while the standard is usually 1-2 years.' 
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1500);
  };

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-8 right-8 z-50 p-4 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-2xl shadow-blue-500/30 transition-all active:scale-95 group"
      >
        <MessageSquare size={24} className="group-hover:rotate-12 transition-transform" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-8 right-8 z-50 w-96 h-[34rem] bg-[#f8fafc] rounded-3xl shadow-2xl shadow-slate-900/10 border border-slate-100 flex flex-col overflow-hidden animate-slideUp">
      {/* Header */}
      <div className="p-5 bg-slate-900 flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center gap-3">
          <BotMessageSquare size={20} className="text-blue-400" />
          <h4 className="text-white font-bold text-sm tracking-tight">LexGuard <span className="text-blue-400">Assistant</span></h4>
        </div>
        <button onClick={() => setIsOpen(false)} className="text-slate-500 hover:text-white transition-colors">
          <X size={18} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 p-6 overflow-y-auto bg-slate-200/50 shadow-inner">
        {messages.map((msg, index) => <Message key={index} {...msg} />)}
      </div>

      {/* Input */}
      <div className="p-4 bg-white border-t border-slate-100">
        <div className="relative flex items-center">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about the non-compete, governing law..." 
            className="w-full pl-5 pr-12 py-3.5 bg-slate-50 border border-slate-100 rounded-full text-xs placeholder:text-slate-400 focus:ring-2 focus:ring-blue-100 focus:border-blue-200 outline-none transition-all"
          />
          <button 
            onClick={handleSend}
            className="absolute right-2 p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors"
          >
            <SendHorizontal size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}