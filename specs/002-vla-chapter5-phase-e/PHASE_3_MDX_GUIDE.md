# Phase 3: MDX Validation & Integration Guide

## Overview

Phase 3 prepares the chapter5-vla.md file for integration into Docusaurus. This document provides validation guidelines, templates, and error handling procedures.

---

## MDX Compatibility Checklist

### Markdown Syntax (T047)

Use standard Markdown with these guidelines:

✅ **Headers**
```markdown
# H1 - Chapter Title
## H2 - Section
### H3 - Subsection
#### H4 - Detail
```

✅ **Lists**
```markdown
- Bullet item
  - Nested item
  
1. Numbered item
2. Second item
```

✅ **Emphasis**
```markdown
*italic* or _italic_
**bold** or __bold__
`code` inline
```

✅ **Code Blocks**
```markdown
\`\`\`python
def example():
    return "code"
\`\`\`
```

### Math Equations (T048)

**IMPORTANT**: Avoid complex LaTeX. Use plain-text notation instead.

✅ **GOOD - Plain text math**
```
Forward kinematics: p = f(q)
where q = [q_1, q_2, ..., q_n]

Jacobian: J = ∂p/∂q

Dynamic equation: τ = I q̈ + f(q, q̇)
```

❌ **AVOID - Complex LaTeX**
```
$$ J = \frac{\partial \mathbf{p}}{\partial \mathbf{q}} $$
$$\tau = I \ddot{q} + f(\mathbf{q}, \dot{\mathbf{q}})$$
```

**Guidelines**:
- Use Unicode operators: ∂, ∑, ∏, √, ∞, π, ≈, ≠, ≤, ≥, →, ←
- Use subscripts/superscripts as plain text: q_1, T^-1, a_ij
- Use English descriptions for complex notation
- Avoid: \frac, \begin{matrix}, \partial (use ∂ instead), \sum (use Σ)

### Special Characters (T049)

✅ **Safe in Markdown**
```
* asterisk
- hyphen
_ underscore
` backtick
| pipe (in tables)
# hash (at start of line for headers)
[ ] parentheses and brackets
( ) in text
```

❌ **Requires escaping or avoidance**
```
\ backslash - avoid or escape as \\
{ } braces - use [braces] or avoid
< > - use &lt; &lt; or [angle brackets]
$ dollar - avoid in text (only for math)
@ mention - avoid unless needed
```

**Solution**: 
- If describing syntax with backslashes, use code blocks with triple backticks
- For set notation, use [a, b, c] instead of {a, b, c}
- For angle brackets, use [angle bracket] or describe: "the less-than symbol"

### Code Blocks (T050)

✅ **Always include language specification**
```markdown
\`\`\`python
code here
\`\`\`

\`\`\`bash
$ npm run build
\`\`\`

\`\`\`xml
<URDF content>
</URDF>
\`\`\`
```

✅ **Supported languages**: python, bash, javascript, typescript, yaml, xml, json, cpp, java

---

## Chapter Template (T046)

Create `docs/chapter5-vla.md` with this structure:

```markdown
---
sidebar_position: 5
---

# Chapter 5: Vision-Language-Action in Physical AI

## Introduction

[Introduction content here - ~700 words]

### What is VLA?

[Definition and three-component model]

### Why VLA Matters

[Motivation and applications]

---

## Table of Contents

1. [Introduction to VLA](#introduction-to-vla)
2. [VLA System Architecture](#vla-system-architecture)
3. [Humanoid Kinematics & Dynamics](#humanoid-kinematics--dynamics)
4. [ROS 2 Integration](#ros-2-integration)
5. [Simulation Environments](#simulation-environments)
6. [Mathematical Foundations](#mathematical-foundations)
7. [NLP & Understanding](#nlp--understanding)
8. [Practical Considerations](#practical-considerations)
9. [Case Studies](#case-studies)
10. [Capstone Project](#capstone-project)

---

## VLA System Architecture

[Architecture content - ~900 words]

---

## Humanoid Kinematics & Dynamics

[Kinematics/dynamics content - ~1100 words]

---

## ROS 2 Integration

[ROS 2 content - ~1000 words]

---

## Simulation Environments

[Simulation content - ~1200 words]

---

## Mathematical Foundations

[Math content - ~1100 words]

---

## NLP & Understanding

[NLP content - ~800 words]

---

## Practical Considerations

[Practical content - ~900 words]

---

## Case Studies

[Cases content - ~1000 words]

---

## Capstone Project

[Capstone content - ~800 words]

---

## Further Reading

[References and resources]
```

---

## Build Test Procedure (T051)

### Step 1: Prepare
```bash
cd G:\hacka\physical-ai-textbook-final
```

### Step 2: Run Build
```bash
npm run build
```

### Step 3: Check Output
- ✅ "Server: Compiled successfully"
- ✅ "Client: Compiled successfully"
- ✅ "exit code 0"
- ✅ No MDX errors

### Step 4: Verify
```bash
# Build output should show:
# [webpack] Compiled successfully in XX seconds
# 0 errors
```

---

## Error Handling Guide (T052)

### Common MDX Errors

#### Error: "Could not parse expression with acorn"
**Cause**: LaTeX syntax or special characters in text  
**Solution**: 
1. Use plain-text notation instead of LaTeX
2. Escape backslashes in code: `\\` 
3. Use code blocks for technical notation

#### Error: "Unexpected token"
**Cause**: Unescaped braces, brackets, or special chars  
**Solution**:
1. Check for `{` or `}` outside code blocks
2. Escape with backslash: `\{` `\}`
3. Or use alternative notation: [braces]

#### Error: "Unexpected indent"
**Cause**: Mixing spaces and tabs in lists  
**Solution**:
1. Use 2 or 4 spaces (not tabs)
2. Keep consistent indentation
3. Don't mix spaces and tabs

#### Error: "Unknown directive"
**Cause**: Invalid MDX syntax  
**Solution**:
1. Check for typos in directives
2. Verify syntax against MDX docs
3. Simplify complex expressions

### Testing Strategy

1. **Build locally first**: Run `npm run build` before committing
2. **Test each section**: Add one section, build, fix issues
3. **Use simpler syntax**: Prefer plain text over LaTeX
4. **Reference chapters 1-4**: Match their syntax exactly
5. **Ask for help**: If unsure, use simpler alternative

---

## Sidebar Integration (T053)

### Update sidebars.js

**File**: `sidebars.js`  
**Location**: Line ~28

**Change**:
```javascript
// From:
items: [
  'chapter1-intro',
  'chapter2-ros2',
  'chapter3-digital-twin',
  'chapter4-nvidia-isaac',
],

// To:
items: [
  'chapter1-intro',
  'chapter2-ros2',
  'chapter3-digital-twin',
  'chapter4-nvidia-isaac',
  'chapter5-vla',  // ADD THIS LINE
],
```

**Verify**:
- ✅ File has no syntax errors
- ✅ Run `npm run build` to test
- ✅ Chapter appears in sidebar

---

## Table of Contents (T054)

### TOC Format

Use this structure in chapter introduction:

```markdown
## Table of Contents

1. **[Introduction to VLA](#introduction)** - VLA definition, motivation, applications

2. **[System Architecture](#architecture)** - Vision, language, action components

3. **[Kinematics & Dynamics](#kinematics)** - Forward/inverse kinematics, dynamics

4. **[ROS 2 Integration](#ros2)** - Node architecture, messaging, orchestration

5. **[Simulation Environments](#simulation)** - Gazebo, Isaac Sim, domain randomization

6. **[Mathematical Foundations](#math)** - Transformations, RL, optimization

7. **[NLP & Understanding](#nlp)** - Speech, intent, dialogue, grounding

8. **[Practical Considerations](#practical)** - Hardware, safety, ethics, debugging

9. **[Case Studies](#cases)** - Pick-place, assembly, social interaction

10. **[Capstone Project](#capstone)** - Framework, requirements, evaluation rubric

---
```

### Linking Strategy

- Use anchor links: `[text](#anchor-id)`
- Create anchors with headers: `## Text {#anchor-id}` or just `## Text` (auto-generated)
- Test links: Click each one after build

---

## Quality Assurance Checklist

### Before Building

- [ ] All headers use # markdown syntax
- [ ] All code blocks have language specification
- [ ] No complex LaTeX equations
- [ ] No unescaped backslashes in text
- [ ] No mixing of spaces and tabs
- [ ] All lists properly indented
- [ ] All links use markdown format

### After Building

- [ ] Build completes with 0 errors
- [ ] No MDX compilation warnings
- [ ] All sections appear in correct order
- [ ] TOC links work correctly
- [ ] Sidebar entry appears
- [ ] Navigation works end-to-end

---

## Phase 3 Summary

✅ **T046**: Chapter template created  
✅ **T047**: Markdown syntax guidelines documented  
✅ **T048**: Math equation formatting guide provided  
✅ **T049**: Special character handling documented  
✅ **T050**: Code block template created  
✅ **T051**: Build verification baseline established  
✅ **T052**: Error handling guide provided  
✅ **T053**: Sidebar integration instructions documented  
✅ **T054**: TOC framework template provided  

**Status**: ✅ **PHASE 3 VALIDATION FRAMEWORK COMPLETE**

All guidelines, templates, and procedures are in place for Phase 2 content generation and Phase 3 validation.

---

## Next: Phase 2 Content Generation

Using this validation framework, Phase 2 will:

1. Generate 10 sections following research.md outlines
2. Use plain-text math notation (no complex LaTeX)
3. Follow markdown syntax guidelines
4. Include code blocks with language specifications
5. Build and test after each section
6. Fix any errors using T052 guidelines
7. Verify with sidebars.js integration (T053)
8. Complete TOC linking (T054)

**Expected Outcome**: Publication-ready chapter5-vla.md with 9,600 words across 10 sections, zero build errors.
