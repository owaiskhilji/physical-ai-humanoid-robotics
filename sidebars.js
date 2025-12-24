// @ts-check

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.

 @type {import('@docusaurus/plugin-content-docs').SidebarsConfig}
 */
const sidebars = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Physical AI Textbook',
      items: [
        'chapter1-intro', // Reference to docs/chapter1-intro.md
        'chapter2-ros2', // Reference to docs/chapter2-ros2.md
        'chapter3-digital-twin', // Reference to docs/chapter3-digital-twin.md
        'chapter4-nvidia-isaac', // Reference to docs/chapter4-nvidia-isaac.md
        'chapter5-vla', // Reference to docs/chapter5-vla.md
      ],
    },
    {
      type: 'category',
      label: 'Tutorial Basics', 
           items: [
        'tutorial-basics/create-a-document',
        'tutorial-basics/create-a-page',
        'tutorial-basics/create-a-blog-post',
        'tutorial-basics/deploy-your-site',
        'tutorial-basics/congratulations', 
         
  
      ],
    },
    {
      type: 'category',
      label: 'Tutorial Extras', // Naya Heading
      items: [
        'tutorial-extras/translate-your-site', 
        'tutorial-extras/manage-docs-versions', 
  
      ],
    },
    {
      type: 'category',
      label: 'Chat Widget Int', // Naya Heading
      items: [
        'chat-widget-documentation'
  
      ],
    },
  ],

  // But you can create a sidebar manually
  /*
  tutorialSidebar: [
    'intro',
    'hello',
    {
      type: 'category',
      label: 'Tutorial',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
   */
};

export default sidebars;
