import React, { useState, useRef, useCallback, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Maximize2, Layers } from 'lucide-react';

const GraphVisualizer = ({ graphData, isSidebarOpen, onToggleSidebar }) => {
  const [hoverNode, setHoverNode] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [hideGranular, setHideGranular] = useState(false);
  
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const containerRef = useRef();
  const fgRef = useRef();

  // Dynamic resizing
  useEffect(() => {
    if (!containerRef.current) return;
    const { clientWidth, clientHeight } = containerRef.current;
    setDimensions({ width: clientWidth, height: clientHeight });
    
    const obs = new ResizeObserver(entries => {
      setDimensions({ width: entries[0].contentRect.width, height: entries[0].contentRect.height });
    });
    obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  const handleNodeHover = useCallback((node) => {
    setHoverNode(node || null);
    if (document.body) {
      document.body.style.cursor = node ? 'pointer' : 'default';
    }
  }, []);

  const handleNodeClick = useCallback((node) => {
    // Pin or unpin the clicked node
    setSelectedNode(prev => (prev && prev.id === node.id) ? null : node);
  }, []);

  const handleMinimize = () => {
    // Extends to full view by dynamically hiding the chatbot sidebar & re-centering graph
    if (onToggleSidebar) onToggleSidebar();
    
    // Ensure the force-graph waits for the CSS transition (300ms) to finish so it can properly re-calculate the new bounding box dimensions
    setTimeout(() => {
      if (fgRef.current) {
        fgRef.current.zoomToFit(400, 50);
      }
    }, 350);
  };

  const getLinkId = (n) => typeof n === 'object' ? n.id : n;

  const drawNode = useCallback((node, ctx, globalScale) => {
    const activeNode = selectedNode || hoverNode;
    const isHovered = activeNode && activeNode.id === node.id;
    
    const isLinked = activeNode && graphData.links.some(l => 
      (getLinkId(l.source) === activeNode.id && getLinkId(l.target) === node.id) || 
      (getLinkId(l.target) === activeNode.id && getLinkId(l.source) === node.id)
    );
    const highlight = isHovered || isLinked;

    // Hide granular overlay behavior: fade out unconnected background nodes
    if (hideGranular && activeNode && !highlight) {
      // Draw very faint
      ctx.beginPath();
      ctx.arc(node.x, node.y, 1.0, 0, 2 * Math.PI, false);
      ctx.fillStyle = 'rgba(239, 246, 255, 0.2)'; 
      ctx.fill();
      return;
    }

    ctx.beginPath();
    // Tiny dots
    ctx.arc(node.x, node.y, 3, 0, 2 * Math.PI, false);
    ctx.fillStyle = highlight ? '#2563eb' : '#eff6ff'; // blue-600 or blue-50
    ctx.fill();
    
    ctx.lineWidth = 1/globalScale;
    
    // Hash property ID to either thin red or thin blue border (like the image)
    const strId = String(node.id || "0");
    const isRed = strId.charCodeAt(strId.length - 1) % 2 === 0;
    
    const outlineColor = highlight ? '#1e3a8a' : (isRed ? '#fca5a5' : '#93c5fd');
    ctx.strokeStyle = outlineColor;
    ctx.stroke();
  }, [hoverNode, selectedNode, hideGranular, graphData.links]);

  const displayNode = selectedNode || hoverNode;

  return (
    <div ref={containerRef} className="w-full h-full relative bg-[#F9F9FB] overflow-hidden">
      
      {/* Absolute Overlays */}
      <div className="absolute top-5 left-5 z-10 flex gap-2.5">
        <button 
          onClick={handleMinimize}
          className="flex items-center gap-2 px-3 py-2 bg-white text-[13px] font-medium rounded-lg shadow-sm border border-gray-200 text-gray-700 hover:bg-gray-50 transition-colors tracking-tight"
        >
          <Maximize2 className="w-3.5 h-3.5" /> {isSidebarOpen ? 'Maximize' : 'Restore Sidebar'}
        </button>
        <button 
          onClick={() => setHideGranular(!hideGranular)}
          className={`flex items-center gap-2.5 px-3 py-2 text-[13px] font-medium rounded-lg shadow-sm transition-colors border tracking-tight ${
            hideGranular 
              ? 'bg-blue-600 border-blue-600 text-white hover:bg-blue-700' 
              : 'bg-[#0F172A] border-[#0F172A] text-white hover:bg-slate-800'
          }`}
        >
          <Layers className={`w-4 h-4 ${hideGranular ? 'text-blue-200' : 'text-gray-400'}`} /> 
          {hideGranular ? 'Show Granular Overlay' : 'Hide Granular Overlay'}
        </button>
      </div>

      {dimensions.width > 0 && (
        <ForceGraph2D
          ref={fgRef}
          width={dimensions.width}
          height={dimensions.height}
          graphData={graphData}
          nodeLabel=""
          nodeRelSize={4}
          nodeCanvasObject={drawNode}
          linkColor={(link) => {
             const activeNode = selectedNode || hoverNode;
             if (activeNode) {
                 const isLinkHighlight = (getLinkId(link.source) === activeNode.id || getLinkId(link.target) === activeNode.id);
                 if (hideGranular && !isLinkHighlight) return 'transparent';
                 return isLinkHighlight ? '#60a5fa' : '#e0f2fe';
             }
             return '#bae6fd';
          }}
          linkWidth={(link) => {
             const activeNode = selectedNode || hoverNode;
             if (activeNode && (getLinkId(link.source) === activeNode.id || getLinkId(link.target) === activeNode.id)) {
                 return 1.5; // Bold the highlighted active links
             }
             return 0.5;
          }}
          onNodeHover={handleNodeHover}
          onNodeClick={handleNodeClick}
          onBackgroundClick={() => setSelectedNode(null)}
          backgroundColor="#F9F9FB"
          d3AlphaDecay={0.02}
          d3VelocityDecay={0.3}
        />
      )}

      {/* Sleek Persistent/Hover Tooltip Dropdown Card */}
      {displayNode && (
        <div 
          className="absolute z-20 bg-white rounded-[12px] shadow-[0_8px_30px_rgb(0,0,0,0.08)] border border-gray-100 p-5 text-[13px] w-[340px] pointer-events-auto transition-opacity"
          style={{ top: '25%', left: '35%', transform: 'translate(-50%, -50%)' }} 
        >
          <div className="flex justify-between items-start mb-3 border-none gap-2">
            <h3 className="font-bold text-[14px] text-gray-900 leading-tight">
              {displayNode.title || displayNode.Entity || displayNode.labels?.[0] || 'Order Info'}
            </h3>
            {selectedNode && selectedNode.id === displayNode.id && (
              <button onClick={() => setSelectedNode(null)} className="text-gray-400 hover:text-gray-900 text-[10px] bg-gray-100 hover:bg-gray-200 px-1.5 py-0.5 rounded-full shrink-0 transition-colors">✕</button>
            )}
          </div>
          <div className="flex flex-col gap-2 text-[12px] text-gray-600">
            {Object.entries(displayNode).map(([key, val]) => {
              if (['x', 'y', 'vx', 'vy', 'index', 'id', 'name', 'Entity'].includes(key)) return null;
              if (typeof val === 'object') return null;
              return (
                <div key={key} className="grid grid-cols-[1fr_1.5fr] gap-2">
                  <span className="font-medium text-[#6b7280] break-words">{key}:</span>
                  <span className="text-[#374151] font-medium text-left break-words">{String(val)}</span>
                </div>
              );
            }).filter(Boolean).slice(0, 12)}
            
            {/* Connected Relationships Edge Tracer */}
            {(() => {
              const cxns = graphData.links.filter(l => getLinkId(l.source) === displayNode.id || getLinkId(l.target) === displayNode.id);
              if (cxns.length === 0) return null;
              return (
                 <div className="mt-3 pt-3 border-t border-gray-100">
                    <h4 className="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-2">Connections ({cxns.length})</h4>
                    <div className="flex flex-col gap-1.5">
                       {cxns.map((c, i) => {
                           const isSource = getLinkId(c.source) === displayNode.id;
                           const pairedId = isSource ? getLinkId(c.target) : getLinkId(c.source);
                           const pairedNode = graphData.nodes.find(n => String(n.id) === String(pairedId)) || { title: pairedId };
                           return (
                               <div key={i} className="text-[11px] bg-slate-50 p-2 rounded border border-slate-100 leading-relaxed shadow-sm">
                                   <span className="text-blue-500 font-semibold tracking-tight">[{c.type || 'LINK'}]</span> {isSource ? '→' : '←'} <span className="font-medium text-slate-700">{pairedNode.title || pairedNode.labels?.[0] || pairedId}</span>
                               </div>
                           );
                       })}
                    </div>
                 </div>
              );
            })()}
          </div>
          <div className="mt-4 text-[11px] text-[#9ca3af] italic font-medium">Additional fields hidden for readability</div>
        </div>
      )}
    </div>
  );
};

export default GraphVisualizer;
