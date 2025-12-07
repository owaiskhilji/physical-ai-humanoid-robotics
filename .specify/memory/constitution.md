<!--
Sync Impact Report:
Version change: Initial → 1.2.0
List of modified principles:
- Technical Accuracy (Added)
- Educational Clarity (Added)
- Free-Tier Architecture (Added)
- Comprehensive Content Structure (Added)
- Strict RAG Chatbot Grounding (Added)
- Sequential Delivery & Documentation (Added)
Added sections:
- Purpose and Scope
- Technical Stack Constraints
- Content Structure & Completeness (Project 1)
- RAG Chatbot Requirements (Project 2 & Bonus)
- Workflow and Execution
Removed sections: None
Templates requiring updates:
- G:\Low-code agent\ai-book\physical-ai\.specify\templates\plan-template.md (✅ updated)
- G:\Low-code agent\ai-book\physical-ai\.specify\templates\spec-template.md (✅ updated)
- G:\Low-code agent\ai-book\physical-ai\.specify\templates\tasks-template.md (✅ updated)
Follow-up TODOs:
- TODO(RATIFICATION_DATE): Original ratification date needs to be determined.
-->
# Physical AI & Humanoid Robotics Textbook (Unified) Constitution

## Purpose and Scope
Create a high-quality, professional AI-Native textbook based on the Physical AI & Humanoid Robotics course, integrated with a functional RAG Chatbot, and structured to support all bonus features (Auth/Personalization/Translation).

## I. Core Principles (Non-Negotiable)

### Technical Accuracy
All content must be technically verified and aligned with the course's stated technologies: ROS 2, Gazebo, NVIDIA Isaac, and VLA concepts.

### Educational Clarity
The tone must be simple, educational, and structured for beginners.

### Free-Tier Architecture
The entire technical solution (DBs, APIs, LLMs) must prioritize free-tier service constraints.

### Comprehensive Content Structure
The textbook must adhere to the specified chapter structure and titles. Detailed topics (sub-sections) for each module must be included in the Specification/Plan. Full, detailed content must be generated for all chapters.

### Strict RAG Chatbot Grounding
The RAG Chatbot must ONLY answer questions based on the published book text. It must also include a 'Selected Text Mode' where the user highlights text on the page, and the chatbot answers only from that highlighted text. The system must include the placeholder structure for all optional features (Auth/Signup, Personalization, Urdu Translation, Subagents). Backend code must follow modular architecture and use FastAPI security best practices.

### Sequential Delivery & Documentation
Focus first on Project 1 (Textbook Content), then Project 2 (Chatbot). All major architectural decisions must be documented.

## II. Technical Stack Constraints

### Frontend/Content
Strictly use Docusaurus.

### Backend/API
Use FastAPI for all RAG/Auth service endpoints.

### Database Architecture
Use the specified stack: Neon Serverless Postgres and Qdrant Cloud Free Tier.

### AI/RAG
Use Gemini for LLM execution (to honor free-tier) but maintain OpenAI/ChatKit SDK integration structure.

## III. Content Structure & Completeness (Project 1)

### Chapter Structure & Titles
The book must use the following official chapter titles:
*   Chapter 1: Introduction & Why Physical AI Matters (Includes Focus/Theme, Goal, Why Matters).
*   Chapter 2: The Robotic Nervous System (ROS 2 Fundamentals).
*   Chapter 3: The Digital Twin (Gazebo & Unity Simulation).
*   Chapter 4: The AI-Robot Brain (NVIDIA Isaac Platform).
*   Chapter 5: Vision-Language-Action (VLA).
*   Chapter 6: Hardware Requirements & Architecture (Appendix).

### Detail Requirements
The Weekly Breakdown and detailed topics (sub-sections) for each module must be included in the Specification/Plan (the next step).

### Quality
Generate full, detailed content for all chapters.

## IV. RAG Chatbot Requirements (Project 2 & Bonus)

### Strict Grounding
The RAG Chatbot must ONLY answer questions based on the published book text.

### Selected Text Mode
The chatbot must also include a 'Selected Text Mode' where the user highlights text on the page, and the chatbot answers only from that highlighted text (Requirement #2).

### Feature Integration
The system must include the placeholder structure for all optional features (Auth/Signup, Personalization, Urdu Translation, Subagents).

### Code Quality
Backend code must follow modular architecture and use FastAPI security best practices.

## V. Workflow and Execution

### Sequential Delivery
Focus first on Project 1 (Textbook Content), then Project 2 (Chatbot).

### Documentation
All major architectural decisions must be documented.

## Governance

This constitution supersedes all other project practices.
Amendments require documentation, approval, and a migration plan.
All Pull Requests and code reviews must verify compliance with these principles.
Any increased complexity must be justified by clear benefits.

**Version**: 1.2.0 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2025-12-04