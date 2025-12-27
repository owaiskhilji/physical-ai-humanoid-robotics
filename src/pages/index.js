import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './index.module.css';
import { motion } from 'framer-motion';
import AnimatedHeroBackground from '@site/src/components/ParticleBackground';
import InteractiveTimeline from '@site/src/components/InteractiveTimeline';

// Modern hero section with gradient background
function HeroSection() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={styles.heroSection}>
      <AnimatedHeroBackground />
      <div className="container relative" style={{ position: 'relative', zIndex: 10 }}>
        <motion.div
          className={styles.heroContent}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className={styles.heroText}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <h1 className={styles.heroTitle}>
              {siteConfig.title}
            </h1>
            <p className={styles.heroSubtitle}>
              {siteConfig.tagline}
            </p>
            <div className={styles.heroButtons}>
              <Link className="button button--primary button--lg interactive-element neon-glow" to="/docs/intro">
                Get Started
              </Link>
              <Link className="button button--secondary button--lg interactive-element neon-glow-green" to="/docs/chapter2-ros2">
                Explore Content
              </Link>
            </div>
          </motion.div>
          <motion.div
            className={styles.heroImage}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            <div className={`${styles.robotPlaceholder} glass`}>
              <svg width="300" height="200" viewBox="0 0 300 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="50" y="50" width="200" height="100" rx="10" fill="#00d4ff" opacity="0.2"/>
                <circle cx="100" cy="80" r="8" fill="#00d4ff"/>
                <circle cx="200" cy="80" r="8" fill="#00d4ff"/>
                <rect x="120" y="100" width="60" height="20" rx="4" fill="#39ff14" opacity="0.5"/>
                <path d="M150 120 L130 140 M150 120 L170 140" stroke="#00d4ff" strokeWidth="3"/>
              </svg>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </header>
  );
}

// What is Physical AI section
function WhatIsPhysicalAISection() {
  return (
    <section className={styles.section}>
      <div className="container">
        <motion.div
          className="row"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.8 }}
        >
          <div className="col col--12">
            <Heading as="h2" className={styles.sectionTitle}>
              What is Physical AI?
            </Heading>
            <p className={styles.sectionDescription}>
              Physical AI represents the convergence of artificial intelligence and robotics,
              enabling machines to perceive, reason, and act in the physical world. Unlike
              traditional AI that operates in digital spaces, Physical AI systems interact
              with tangible objects and environments through sensors, actuators, and
              sophisticated control algorithms.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// Key Features section
function KeyFeaturesSection() {
  const features = [
    {
      title: 'Embodied Intelligence',
      description: 'AI systems that understand and interact with the physical world through sensors and actuators.',
      icon: '🤖'
    },
    {
      title: 'Real-time Perception',
      description: 'Advanced computer vision and sensor fusion for understanding dynamic environments.',
      icon: '👁️'
    },
    {
      title: 'Adaptive Control',
      description: 'Machine learning algorithms that adapt to changing physical conditions and tasks.',
      icon: '🔄'
    },
    {
      title: 'Human-Robot Interaction',
      description: 'Natural interfaces enabling seamless collaboration between humans and robots.',
      icon: '🤝'
    }
  ];

  return (
    <section className={styles.section}>
      <div className="container">
        <motion.div
          className="row"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.8 }}
        >
          <div className="col col--12">
            <Heading as="h2" className={styles.sectionTitle}>
              Key Features
            </Heading>
          </div>
        </motion.div>
        <div className="row">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className="col col--3"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <div className={`${styles.featureCard} glass interactive-element neon-glow`}>
                <div className={styles.featureIcon}>{feature.icon}</div>
                <h3 className={styles.featureTitle}>{feature.title}</h3>
                <p className={styles.featureDescription}>{feature.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// Humanoid Robotics Roadmap section
function HumanoidRoadmapSection() {
  return (
    <section className={styles.section}>
      <div className="container">
        <motion.div
          className="row"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.8 }}
        >
          <div className="col col--12">
            <Heading as="h2" className={styles.sectionTitle}>
              Humanoid Robotics Roadmap
            </Heading>
          </div>
        </motion.div>
        <div className="row">
          <div className="col col--12">
            <InteractiveTimeline />
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Physical AI & Humanoid Robotics`}
      description="Advanced AI systems for physical interaction and humanoid robotics">
      <HeroSection />
      <WhatIsPhysicalAISection />
      <KeyFeaturesSection />
      <HumanoidRoadmapSection />
    </Layout>
  );
}
