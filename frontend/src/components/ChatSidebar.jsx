import React, { useState, useRef, useEffect } from 'react';
import { User, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const ChatSidebar = ({ messages, onSendMessage, isLoading }) => {
  const [inputVal, setInputVal] = useState('');
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputVal.trim() || isLoading) return;
    onSendMessage(inputVal);
    setInputVal('');
  };

  return (
    <div className="flex flex-col h-full bg-white relative">
      <div className="px-5 py-4 border-b border-gray-100 shrink-0">
        <h2 className="font-semibold text-[15px] text-gray-900 tracking-tight">Chat with Graph</h2>
        <p className="text-[12.5px] text-gray-500 mt-1 font-medium">Order to Cash</p>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-6 space-y-7 pb-36">
        {messages.map((m, idx) => (
          <div key={idx} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
            {m.role === 'ai' && (
              <div className="flex items-center gap-3 mb-2.5">
                <div className="w-8 h-8 rounded-full bg-[#1e1e1e] flex items-center justify-center text-white shrink-0 shadow-sm">
                  <span className="font-bold text-lg font-serif">D</span>
                </div>
                <div>
                  <div className="text-[14px] font-bold text-[#1f2937] tracking-tight">Dodge AI</div>
                  <div className="text-[11px] text-[#9ca3af] font-medium uppercase tracking-wider mt-0.5">Graph Agent</div>
                </div>
              </div>
            )}
            {m.role === 'user' && (
              <div className="flex items-center gap-3 mb-2.5">
                <div className="text-[14px] font-bold text-[#1f2937] tracking-tight">You</div>
                <div className="w-8 h-8 rounded-full bg-[#b0b0b0] flex items-center justify-center text-white shrink-0 shadow-sm">
                  <User className="w-5 h-5 fill-current" />
                </div>
              </div>
            )}

            <div 
              className={`max-w-[92%] text-[14.5px] p-4 leading-[1.65] ${
                m.role === 'user' 
                  ? 'bg-[#292929] text-white rounded-[14px] rounded-tr-sm shadow-sm font-medium' 
                  : 'bg-transparent text-[#374151] pr-2 pl-0'
              }`}
            >
              {m.role === 'ai' ? (
                <ReactMarkdown 
                  components={{
                    p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                    ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-2 space-y-1 marker:text-gray-400" {...props} />,
                    ol: ({node, ...props}) => <ol className="list-decimal pl-5 mb-2 space-y-1 marker:text-gray-400" {...props} />,
                    li: ({node, ...props}) => <li className="pl-1" {...props} />,
                    strong: ({node, ...props}) => <strong className="font-semibold text-gray-900" {...props} />
                  }}
                >
                  {m.content}
                </ReactMarkdown>
              ) : (
                m.content
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="pl-11 text-[13px] font-medium text-gray-400 flex items-center gap-2">
            <span className="animate-pulse">Analyzing graph logic</span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="absolute bottom-0 left-0 w-full px-4 pb-4 pt-12 bg-gradient-to-t from-white via-white to-transparent shrink-0">
        <div className="bg-white rounded-[14px] border border-gray-200 overflow-hidden shadow-sm flex flex-col focus-within:ring-2 focus-within:ring-gray-200">
          <div className="flex items-center gap-2 px-3 py-2.5 bg-[#f8fafc] border-b border-gray-200 text-[11px] text-gray-500 font-medium">
            <div className={`w-1.5 h-1.5 rounded-full ${isLoading ? 'bg-amber-400' : 'bg-green-500'}`}></div>
            {isLoading ? 'Dodge AI is analyzing...' : 'Dodge AI is awaiting instructions'}
          </div>
          <form onSubmit={handleSubmit} className="relative flex p-1">
            <input 
              type="text" 
              value={inputVal}
              onChange={e => setInputVal(e.target.value)}
              placeholder="Analyze anything"
              className="w-full bg-transparent px-3 py-3 text-[14px] text-gray-800 outline-none placeholder-gray-400"
              disabled={isLoading}
            />
            <button 
              type="submit"
              disabled={isLoading || !inputVal.trim()}
              className="m-1 px-4 py-1.5 bg-[#8C8C8C] text-white text-[13.5px] font-medium rounded-lg hover:bg-gray-500 disabled:opacity-50 disabled:hover:bg-[#8C8C8C] transition-colors shrink-0"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatSidebar;
