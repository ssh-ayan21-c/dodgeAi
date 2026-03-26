import React, { useState, useCallback } from 'react';
import axios from 'axios';
import Header from './components/Header';
import GraphVisualizer from './components/GraphVisualizer';
import ChatSidebar from './components/ChatSidebar';

function App() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hi! I can help you analyze the Order to Cash process.' }
  ]);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const parseGraphData = useCallback((rawRecords) => {
    let newNodes = [];
    let newLinks = [];
    const nodeMap = new Map();

    const processEntity = (ent) => {
      if (ent && typeof ent === 'object' && !Array.isArray(ent)) {
        
        const isLink = ent.source !== undefined && ent.target !== undefined;
        if (isLink) {
             newLinks.push({ source: String(ent.source), target: String(ent.target), type: ent.type || 'LINK' });
        }

        // Isolate primitive properties to determine if this is a genuine node or just an alias wrapper (e.g. {'n': {...}})
        const primitiveKeys = Object.keys(ent).filter(k => ent[k] !== null && typeof ent[k] !== 'object' && !['source', 'target', 'type'].includes(k));
        
        if (primitiveKeys.length > 0 && !isLink) {
            let id = ent.id || ent.element_id || ent.neo4j_id;
            
            // If no native ID, guarantee absolute uniqueness via composite hash so multiple loose objects don't merge
            if (!id) {
                const uniqueStr = primitiveKeys.map(k => String(ent[k])).join('_').substring(0, 100);
                id = `obj_${uniqueStr}_${Math.random().toString(36).substring(2, 7)}`;
            }

            let title = 'Record Info';
            if (ent.labels && ent.labels.length > 0) title = ent.labels[0];
            else {
                // Determine best dynamic title strictly from its properties
                const titleKey = primitiveKeys.find(k => k.toLowerCase().includes('document') || k.toLowerCase().includes('order') || k.toLowerCase().includes('customer') || k.toLowerCase().includes('material') || k.toLowerCase().includes('name') || k.toLowerCase().includes('id'));
                if (titleKey) title = `${titleKey}: ${ent[titleKey]}`;
            }

            if (!nodeMap.has(id)) {
               nodeMap.set(id, { id: String(id), title: title, name: title, ...ent });
            }
        }

        // Always recurse down to aggressively unwrap nested Neo4j aliases (e.g., {'n': {id: 123}, 'r': {...}})
        Object.values(ent).forEach(v => {
             if (v && typeof v === 'object') processEntity(v);
        });
        
      } else if (Array.isArray(ent)) {
         ent.forEach(processEntity);
      }
    };

    if (Array.isArray(rawRecords)) {
      rawRecords.forEach(record => {
        processEntity(record);
      });
    }

    newNodes = Array.from(nodeMap.values());
    
    // To generate neat visualization even without explicit edges returned from AI, 
    // we can implement a fallback layout, but force graph works with floating nodes too.
    setGraphData({ nodes: newNodes, links: newLinks });
  }, []);

  const handleSendMessage = async (userText) => {
    const newMsg = { role: 'user', content: userText };
    setMessages(prev => [...prev, newMsg]);
    setIsLoading(true);

    try {
      // Connect to the Phase 3 backend
      const response = await axios.post('https://dodgeai-f4om.onrender.com/api/chat', { question: userText });
      const { answer, graph_data } = response.data;
      
      setMessages(prev => [...prev, { role: 'ai', content: answer }]);
      parseGraphData(graph_data);
    } catch (error) {
      console.error("API Error:", error);
      setMessages(prev => [...prev, { role: 'ai', content: 'Sorry, the Graph Protocol Engine encountered an error connecting to the database.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen w-full bg-white text-slate-800 font-sans">
      <Header />
      <div className="flex flex-1 overflow-hidden relative">
        <div className={`${isSidebarOpen ? 'w-[75%]' : 'w-full'} relative h-full bg-[#f8fafc] transition-all duration-300 ease-in-out`}>
          <GraphVisualizer 
             graphData={graphData} 
             isSidebarOpen={isSidebarOpen} 
             onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} 
          />
        </div>
        <div 
          className={`${isSidebarOpen ? 'translate-x-0 w-[25%]' : 'translate-x-full w-0'} absolute right-0 h-full border-l border-gray-200 bg-white flex flex-col shadow-xl transition-all duration-300 ease-in-out z-10 overflow-hidden block`}
        >
          {isSidebarOpen && (
             <ChatSidebar 
               messages={messages} 
               onSendMessage={handleSendMessage} 
               isLoading={isLoading} 
             />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
