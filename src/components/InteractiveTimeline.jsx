import React, { useState } from 'react';
import { motion } from 'framer-motion';

const InteractiveTimeline = () => {
  const [activeIndex, setActiveIndex] = useState(0);

  const timelineItems = [
    {
      phase: 'Phase 1',
      title: 'Basic Mobility',
      description: 'Stable bipedal walking and basic manipulation',
      status: 'completed',
      date: '2024'
    },
    {
      phase: 'Phase 2',
      title: 'Enhanced Perception',
      description: 'Advanced vision and environment understanding',
      status: 'inProgress',
      date: '2025'
    },
    {
      phase: 'Phase 3',
      title: 'Complex Tasks',
      description: 'Multi-step task execution and human collaboration',
      status: 'planned',
      date: '2026'
    },
    {
      phase: 'Phase 4',
      title: 'Autonomous Operation',
      description: 'Long-term autonomous operation in real-world settings',
      status: 'planned',
      date: '2027'
    }
  ];

  return (
    <div className="timeline-container">
      <div className="timeline">
        {timelineItems.map((item, index) => (
          <div
            key={index}
            className={`timeline-item ${activeIndex === index ? 'active' : ''}`}
            onClick={() => setActiveIndex(index)}
          >
            <motion.div
              className={`timeline-card glass interactive-element ${activeIndex === index ? 'neon-glow' : 'neon-glow-green'}`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <div className="timeline-date">{item.date}</div>
              <div className={`timeline-status ${item.status}`}>{item.status}</div>
              <h3 className="timeline-title">{item.title}</h3>
              <p className="timeline-description">{item.description}</p>
            </motion.div>

            {/* Timeline connector */}
            {index < timelineItems.length - 1 && (
              <div className="timeline-connector">
                <div className="connector-line">
                  <div className="connector-fill"></div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default InteractiveTimeline;