import React from 'react';

interface NetworkVisualizationProps {
  onNodeClick: (nodeName: string) => void;
  currentView: 'topLevel' | 'randomProcesses';
}

const NetworkVisualization: React.FC<NetworkVisualizationProps> = ({ onNodeClick, currentView }) => {
  const TopLevelView = (
    <>
      {/* Core Concepts Group */}
      {/* Vector Spaces Node */}
      <g 
        transform="translate(200,300)" 
        onClick={() => onNodeClick('Vector Spaces')}
        className="cursor-pointer hover:opacity-75 transition-opacity"
      >
        <circle 
          r="50" 
          fill="url(#nodeGradient)"
          stroke="#64748b"
          strokeWidth="2"
          className="transition-all hover:stroke-blue-500"
        />
        <text 
          textAnchor="middle" 
          y="-8"
          className="text-sm font-medium select-none pointer-events-none"
        >
          Vector
        </text>
        <text 
          textAnchor="middle" 
          y="8"
          className="text-sm font-medium select-none pointer-events-none"
        >
          Spaces
        </text>
        <circle r="8" cy="-35" fill="#3b82f6" className="pointer-events-none" />
        <text 
          textAnchor="middle" 
          y="-32"
          fill="white"
          className="text-xs select-none pointer-events-none"
        >
          4
        </text>
      </g>

      {/* Random Processes Node */}
      <g 
        transform="translate(400,300)"
        onClick={() => onNodeClick('Random Processes')}
        className="cursor-pointer hover:opacity-75 transition-opacity"
      >
        <circle 
          r="45" 
          fill="url(#nodeGradient)"
          stroke="#64748b"
          strokeWidth="2"
          className="transition-all hover:stroke-blue-500"
        />
        <text 
          textAnchor="middle" 
          y="-8"
          className="text-sm font-medium select-none pointer-events-none"
        >
          Random
        </text>
        <text 
          textAnchor="middle" 
          y="8"
          className="text-sm font-medium select-none pointer-events-none"
        >
          Processes
        </text>
        <circle r="8" cy="-30" fill="#3b82f6" className="pointer-events-none" />
        <text 
          textAnchor="middle" 
          y="-27"
          fill="white"
          className="text-xs select-none pointer-events-none"
        >
          3
        </text>
      </g>

      {/* Other top-level nodes remain the same... */}
      {/* Edges */}
      <path 
        d="M 200,300 C 300,300 300,300 400,300" 
        fill="none" 
        stroke="#94a3b8" 
        strokeWidth="2"
        markerEnd="url(#arrowhead)"
        className="transition-all hover:stroke-blue-400"
      />
      {/* Other edges remain the same... */}
    </>
  );

  const RandomProcessesView = (
    <>
      {/* Central Random Processes Node */}
      <g 
        transform="translate(400,300)"
        onClick={() => onNodeClick('Random Processes')}
        className="cursor-pointer hover:opacity-75 transition-opacity"
      >
        <circle 
          r="60" 
          fill="url(#nodeGradient)"
          stroke="#64748b"
          strokeWidth="2"
          className="transition-all hover:stroke-blue-500"
        />
        <text 
          textAnchor="middle" 
          y="-8"
          className="text-sm font-medium select-none pointer-events-none"
        >
          Random
        </text>
        <text 
          textAnchor="middle" 
          y="8"
          className="text-sm font-medium select-none pointer-events-none"
        >
          Processes
        </text>
      </g>

      {/* Stochastic Processes Node */}
      <g 
        transform="translate(200,200)"
        onClick={() => onNodeClick('Stochastic Processes')}
        className="cursor-pointer hover:opacity-75 transition-opacity"
      >
        <circle 
          r="45" 
          fill="url(#nodeGradient)"
          stroke="#64748b"
          strokeWidth="2"
          className="transition-all hover:stroke-blue-500"
        />
        <text 
          textAnchor="middle" 
          y="-8"
          className="text-sm font-medium select-none pointer-events-none"
        >
          Stochastic
        </text>
        <text 
          textAnchor="middle" 
          y="8"
          className="text-sm font-medium select-none pointer-events-none"
        >
          Processes
        </text>
      </g>

      {/* Time Series Node */}
      <g 
        transform="translate(200,400)"
        onClick={() => onNodeClick('Time Series')}
        className="cursor-pointer hover:opacity-75 transition-opacity"
      >
        <circle 
          r="45" 
          fill="url(#nodeGradient)"
          stroke="#64748b"
          strokeWidth="2"
          className="transition-all hover:stroke-blue-500"
        />
        <text 
          textAnchor="middle" 
          y="0"
          className="text-sm font-medium select-none pointer-events-none"
        >
          Time Series
        </text>
      </g>

      {/* Markov Processes Node */}
      <g 
        transform="translate(600,200)"
        onClick={() => onNodeClick('Markov Processes')}
        className="cursor-pointer hover:opacity-75 transition-opacity"
      >
        <circle 
          r="45" 
          fill="url(#nodeGradient)"
          stroke="#64748b"
          strokeWidth="2"
          className="transition-all hover:stroke-blue-500"
        />
        <text 
          textAnchor="middle" 
          y="-8"
          className="text-sm font-medium select-none pointer-events-none"
        >
          Markov
        </text>
        <text 
          textAnchor="middle" 
          y="8"
          className="text-sm font-medium select-none pointer-events-none"
        >
          Processes
        </text>
      </g>

      {/* Gaussian Processes Node */}
      <g 
        transform="translate(600,400)"
        onClick={() => onNodeClick('Gaussian Processes')}
        className="cursor-pointer hover:opacity-75 transition-opacity"
      >
        <circle 
          r="45" 
          fill="url(#nodeGradient)"
          stroke="#64748b"
          strokeWidth="2"
          className="transition-all hover:stroke-blue-500"
        />
        <text 
          textAnchor="middle" 
          y="-8"
          className="text-sm font-medium select-none pointer-events-none"
        >
          Gaussian
        </text>
        <text 
          textAnchor="middle" 
          y="8"
          className="text-sm font-medium select-none pointer-events-none"
        >
          Processes
        </text>
      </g>

      {/* Connecting Edges */}
      <path 
        d="M 400,300 C 350,250 250,200 200,200" 
        fill="none" 
        stroke="#94a3b8" 
        strokeWidth="2"
        markerEnd="url(#arrowhead)"
        className="transition-all hover:stroke-blue-400"
      />
      <path 
        d="M 400,300 C 350,350 250,400 200,400" 
        fill="none" 
        stroke="#94a3b8" 
        strokeWidth="2"
        markerEnd="url(#arrowhead)"
        className="transition-all hover:stroke-blue-400"
      />
      <path 
        d="M 400,300 C 450,250 550,200 600,200" 
        fill="none" 
        stroke="#94a3b8" 
        strokeWidth="2"
        markerEnd="url(#arrowhead)"
        className="transition-all hover:stroke-blue-400"
      />
      <path 
        d="M 400,300 C 450,350 550,400 600,400" 
        fill="none" 
        stroke="#94a3b8" 
        strokeWidth="2"
        markerEnd="url(#arrowhead)"
        className="transition-all hover:stroke-blue-400"
      />
    </>
  );

  return (
    <svg viewBox="0 0 800 600" className="w-full h-full">
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon points="0 0, 10 3.5, 0 7" fill="#94a3b8" />
        </marker>
        
        <linearGradient id="nodeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#e2e8f0" />
          <stop offset="100%" stopColor="#cbd5e1" />
        </linearGradient>
      </defs>

      {currentView === 'topLevel' ? TopLevelView : RandomProcessesView}
    </svg>
  );
};

export default NetworkVisualization;