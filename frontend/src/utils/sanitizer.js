/**
 * HTML Sanitization Utility
 * Prevents XSS attacks by sanitizing user-generated content
 */

import DOMPurify from 'dompurify';

// Configure DOMPurify for safe HTML
const config = {
  // Allow basic formatting tags
  ALLOWED_TAGS: [
    'b', 'i', 'em', 'strong', 'u', 'p', 'br', 'span', 'div',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'a', 'blockquote', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td'
  ],

  // Allow safe attributes
  ALLOWED_ATTR: [
    'href', 'target', 'rel', 'class', 'id',
    'style' // Will be filtered by ALLOWED_STYLES
  ],

  // Only allow specific styles to prevent CSS injection
  ALLOWED_STYLES: {
    'color': true,
    'background-color': true,
    'font-weight': true,
    'font-style': true,
    'text-decoration': true,
    'text-align': true
  },

  // Force all links to open in new tab with noopener
  ADD_ATTR: ['target', 'rel'],

  // Remove dangerous elements completely
  FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'form', 'input', 'button'],

  // Remove dangerous attributes
  FORBID_ATTR: ['onerror', 'onclick', 'onload', 'onmouseover', 'onfocus', 'onblur']
};

// Strict config for user messages (no HTML at all)
const strictConfig = {
  ALLOWED_TAGS: [],
  ALLOWED_ATTR: [],
  KEEP_CONTENT: true // Keep text content but strip all HTML
};

/**
 * Sanitize HTML content to prevent XSS attacks
 * @param {string} dirty - The potentially dangerous HTML string
 * @param {boolean} strict - If true, strips ALL HTML tags
 * @returns {string} - The sanitized HTML string
 */
export function sanitizeHTML(dirty, strict = false) {
  if (!dirty) return '';

  // For strict mode, remove all HTML
  if (strict) {
    return DOMPurify.sanitize(dirty, strictConfig);
  }

  // Apply standard sanitization
  let clean = DOMPurify.sanitize(dirty, config);

  // Additional security: ensure links have rel="noopener noreferrer"
  if (clean.includes('<a ')) {
    clean = clean.replace(/<a /g, '<a rel="noopener noreferrer" target="_blank" ');
  }

  return clean;
}

/**
 * Sanitize plain text (escapes all HTML)
 * Use this when you want to display user input as plain text
 * @param {string} text - The text to escape
 * @returns {string} - HTML-escaped text
 */
export function escapeHTML(text) {
  if (!text) return '';

  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Sanitize markdown content (converts to HTML then sanitizes)
 * @param {string} markdown - Markdown content
 * @returns {string} - Sanitized HTML
 */
export function sanitizeMarkdown(markdown) {
  if (!markdown) return '';

  // Basic markdown to HTML conversion (for common cases)
  let html = markdown
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
    .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
    .replace(/\n/g, '<br>') // Line breaks
    .replace(/^### (.*?)$/gm, '<h3>$1</h3>') // H3
    .replace(/^## (.*?)$/gm, '<h2>$1</h2>') // H2
    .replace(/^# (.*?)$/gm, '<h1>$1</h1>'); // H1

  // Sanitize the converted HTML
  return sanitizeHTML(html);
}

/**
 * Create a Vue directive for sanitized HTML
 */
export const vSanitizeHtml = {
  beforeUpdate(el, binding) {
    el.innerHTML = sanitizeHTML(binding.value);
  },
  mounted(el, binding) {
    el.innerHTML = sanitizeHTML(binding.value);
  }
};

/**
 * Check if a string contains potentially dangerous content
 * @param {string} content - Content to check
 * @returns {boolean} - True if dangerous content detected
 */
export function containsDangerousContent(content) {
  if (!content) return false;

  const dangerous = [
    '<script', '</script',
    'javascript:', 'data:text/html',
    'onerror=', 'onclick=', 'onload=',
    '<iframe', '<object', '<embed',
    'eval(', 'setTimeout(', 'setInterval(',
    '.innerHTML', '.outerHTML',
    'document.write', 'document.cookie'
  ];

  const lowerContent = content.toLowerCase();
  return dangerous.some(pattern => lowerContent.includes(pattern));
}

// Export as default for convenience
export default {
  sanitizeHTML,
  escapeHTML,
  sanitizeMarkdown,
  vSanitizeHtml,
  containsDangerousContent
};