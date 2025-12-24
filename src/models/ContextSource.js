/**
 * ContextSource model representing a reference to documentation content
 * Based on data-model.md specification
 */

/**
 * Creates a ContextSource object
 * @param {string} id - Unique identifier for the source
 * @param {string} title - Title of the documentation section
 * @param {string} url - URL to the documentation section
 * @param {string} [excerpt] - Brief excerpt from the source content
 * @param {string} [pageId] - ID of the documentation page
 * @param {number} [confidence] - Confidence score of the source relevance (0-1)
 * @returns {Object} ContextSource object
 */
export const createContextSource = (id, title, url, excerpt = '', pageId = '', confidence = null) => {
  // Validate required fields
  if (!id || typeof id !== 'string') {
    throw new Error('ContextSource id is required and must be a string');
  }

  if (!title || typeof title !== 'string') {
    throw new Error('ContextSource title is required and must be a string');
  }

  if (!url || typeof url !== 'string') {
    throw new Error('ContextSource url is required and must be a string');
  }

  // Validate URL format (basic check for relative or absolute HTTPS)
  if (!url.startsWith('/') && !url.startsWith('https://') && !url.startsWith('http://')) {
    throw new Error('ContextSource url must be a relative path or absolute HTTPS/HTTP URL');
  }

  // Validate confidence if provided
  if (confidence !== null && (typeof confidence !== 'number' || confidence < 0 || confidence > 1)) {
    throw new Error('ContextSource confidence must be a number between 0 and 1, or null');
  }

  // Validate title is not empty
  if (!title.trim()) {
    throw new Error('ContextSource title must not be empty');
  }

  return {
    id,
    title,
    url,
    excerpt,
    pageId,
    confidence
  };
};

/**
 * Validates a ContextSource object
 * @param {Object} source - The ContextSource object to validate
 * @returns {boolean} Whether the source is valid
 */
export const validateContextSource = (source) => {
  try {
    if (!source || typeof source !== 'object') {
      return false;
    }

    // Check required fields
    if (!source.id || typeof source.id !== 'string') {
      return false;
    }

    if (!source.title || typeof source.title !== 'string' || !source.title.trim()) {
      return false;
    }

    if (!source.url || typeof source.url !== 'string') {
      return false;
    }

    // Validate URL format
    if (!source.url.startsWith('/') && !source.url.startsWith('https://') && !source.url.startsWith('http://')) {
      return false;
    }

    // Validate optional fields if present
    if (source.excerpt && typeof source.excerpt !== 'string') {
      return false;
    }

    if (source.pageId && typeof source.pageId !== 'string') {
      return false;
    }

    if (source.confidence !== null && source.confidence !== undefined) {
      if (typeof source.confidence !== 'number' || source.confidence < 0 || source.confidence > 1) {
        return false;
      }
    }

    return true;
  } catch (error) {
    console.error('Error validating ContextSource:', error);
    return false;
  }
};

/**
 * Creates a ContextSource from a plain object (e.g., from API response)
 * @param {Object} obj - Plain object to convert to ContextSource
 * @returns {Object} Validated ContextSource object
 */
export const contextSourceFromObject = (obj) => {
  if (!obj || typeof obj !== 'object') {
    throw new Error('Input must be a valid object');
  }

  const {
    id,
    title,
    url,
    excerpt = '',
    pageId = '',
    confidence = null
  } = obj;

  return createContextSource(id, title, url, excerpt, pageId, confidence);
};

/**
 * Validates an array of ContextSource objects
 * @param {Array} sources - Array of ContextSource objects to validate
 * @returns {boolean} Whether all sources are valid
 */
export const validateContextSources = (sources) => {
  if (!Array.isArray(sources)) {
    return false;
  }

  return sources.every(source => validateContextSource(source));
};