/**
 * Currency formatting utilities for input fields
 * Provides real-time comma formatting as users type
 */

/**
 * Formats a number as currency with commas (no dollar sign)
 * @param {number} value - The numeric value to format
 * @returns {string} Formatted string with commas
 */
export const formatCurrency = (value) => {
  if (value === null || value === undefined || value === 0) return '0';
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(value);
};

/**
 * Formats a number as full currency with dollar sign
 * @param {number} value - The numeric value to format
 * @returns {string} Formatted currency string
 */
export const formatCurrencyDisplay = (value) => {
  if (value === null || value === undefined || value === 0) return '$0';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(value);
};

/**
 * Currency input event handlers for Vue components
 */
export const createCurrencyHandlers = (updateCallback) => {
  const rawValues = {};
  
  return {
    // Store raw values for each field
    rawValues,
    
    /**
     * Handle focus event - show raw numeric value for editing
     */
    onFocus: (field, currentValue) => {
      if (!currentValue || currentValue === 0) {
        rawValues[field] = '';
      } else {
        rawValues[field] = currentValue.toString();
      }
    },

    /**
     * Handle input event - format as user types
     */
    onInput: (event, field) => {
      // Remove non-numeric characters except decimal
      let raw = event.target.value.replace(/[^0-9.]/g, '');
      
      // Handle multiple decimals - only allow one
      const parts = raw.split('.');
      if (parts.length > 2) {
        raw = parts[0] + '.' + parts[1];
      }
      
      // Limit decimal places to 2
      if (parts[1] && parts[1].length > 2) {
        raw = parts[0] + '.' + parts[1].slice(0, 2);
      }
      
      // Handle edge cases
      if (raw === '.') {
        rawValues[field] = '0.';
        updateCallback(field, 0);
        return;
      }
      
      if (raw === '') {
        rawValues[field] = '';
        updateCallback(field, 0);
        return;
      }
      
      // Format the display value with commas
      const numericValue = parseFloat(raw) || 0;
      const formattedValue = formatCurrency(numericValue);
      
      // Update the display and model
      rawValues[field] = formattedValue;
      updateCallback(field, numericValue);
      
      // Update the input display
      event.target.value = formattedValue;
    },

    /**
     * Handle blur event - final formatting
     */
    onBlur: (field, currentValue) => {
      rawValues[field] = formatCurrency(currentValue || 0);
    },

    /**
     * Get the display value for a field
     */
    getDisplayValue: (field, currentValue) => {
      return rawValues[field] !== undefined ? rawValues[field] : formatCurrency(currentValue || 0);
    }
  };
};