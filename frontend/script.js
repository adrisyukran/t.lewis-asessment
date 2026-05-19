/**
 * Campaign Analyzer - Frontend Script
 * Handles form submission, API calls, and results display
 */

// API Configuration
const API_BASE_URL = 'http://localhost:5000';
const ANALYZE_ENDPOINT = '/api/analyze';

// DOM Elements
const elements = {
    form: null,
    reportFile: null,
    guidelinesFile: null,
    reportFileName: null,
    guidelinesFileName: null,
    analyzeButton: null,
    loadingOverlay: null,
    errorContainer: null,
    errorText: null,
    errorDismiss: null,
    resultsSection: null,
    metricsGrid: null,
    metricSpend: null,
    metricRoas: null,
    metricCtr: null,
    metricImpressions: null,
    comparisonText: null,
    guidelinesList: null,
    redFlagText: null,
    opportunityText: null,
    summaryText: null
};

// State
let isLoading = false;

/**
 * Initialize DOM element references
 */
function initializeElements() {
    elements.form = document.getElementById('analyzeForm');
    elements.reportFile = document.getElementById('reportFile');
    elements.guidelinesFile = document.getElementById('guidelinesFile');
    elements.reportFileName = document.getElementById('reportFileName');
    elements.guidelinesFileName = document.getElementById('guidelinesFileName');
    elements.analyzeButton = document.getElementById('analyzeButton');
    elements.loadingOverlay = document.getElementById('loadingOverlay');
    elements.errorContainer = document.getElementById('errorContainer');
    elements.errorText = document.getElementById('errorText');
    elements.errorDismiss = document.getElementById('errorDismiss');
    elements.resultsSection = document.getElementById('resultsSection');
    elements.metricSpend = document.getElementById('metricSpend');
    elements.metricRoas = document.getElementById('metricRoas');
    elements.metricCtr = document.getElementById('metricCtr');
    elements.metricImpressions = document.getElementById('metricImpressions');
    elements.comparisonText = document.getElementById('comparisonText');
    elements.guidelinesList = document.getElementById('guidelinesList');
    elements.redFlagText = document.getElementById('redFlagText');
    elements.opportunityText = document.getElementById('opportunityText');
    elements.summaryText = document.getElementById('summaryText');
}

/**
 * Format number with proper separators and decimals
 * @param {number} value - The number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted number string
 */
function formatNumber(value, decimals = 2) {
    if (value === null || value === undefined || isNaN(value)) {
        return '--';
    }
    
    const num = Number(value);
    
    // For large numbers, use compact notation
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    
    return num.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

/**
 * Format currency value
 * @param {number} value - The currency value
 * @returns {string} Formatted currency string
 */
function formatCurrency(value) {
    if (value === null || value === undefined || isNaN(value)) {
        return '--';
    }
    
    return '$' + Number(value).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

/**
 * Format percentage value
 * @param {number} value - The percentage value
 * @returns {string} Formatted percentage string
 */
function formatPercentage(value) {
    if (value === null || value === undefined || isNaN(value)) {
        return '--';
    }
    
    return Number(value).toFixed(2) + '%';
}

// Loading status messages for dynamic feedback
const LOADING_MESSAGES = [
    'Extracting text from report...',
    'Cleaning OCR errors...',
    'Retrieving brand guidelines...',
    'Performing agentic analysis...',
    'Finalizing recommendations...'
];

// Interval reference for clearing
let loadingInterval = null;
let currentMessageIndex = 0;

/**
 * Update loading text with dynamic status
 */
function updateLoadingStatus() {
    const loadingText = elements.loadingOverlay.querySelector('.loading-text');
    if (loadingText) {
        loadingText.textContent = LOADING_MESSAGES[currentMessageIndex];
        currentMessageIndex = (currentMessageIndex + 1) % LOADING_MESSAGES.length;
    }
}

/**
 * Show loading overlay with dynamic status updates
 */
function showLoading() {
    isLoading = true;
    currentMessageIndex = 0;
    elements.loadingOverlay.classList.add('active');
    elements.analyzeButton.disabled = true;
    
    // Set initial message immediately
    const loadingText = elements.loadingOverlay.querySelector('.loading-text');
    if (loadingText) {
        loadingText.textContent = LOADING_MESSAGES[0];
    }
    
    // Start cycling through messages every 2.5 seconds
    loadingInterval = setInterval(updateLoadingStatus, 2500);
}

/**
 * Hide loading overlay and stop status updates
 */
function hideLoading() {
    // Clear the interval when loading completes
    if (loadingInterval) {
        clearInterval(loadingInterval);
        loadingInterval = null;
    }
    isLoading = false;
    elements.loadingOverlay.classList.remove('active');
    elements.analyzeButton.disabled = false;
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    elements.errorText.textContent = message;
    elements.errorContainer.classList.add('active');
}

/**
 * Hide error message
 */
function hideError() {
    elements.errorContainer.classList.remove('active');
}

/**
 * Show results section
 */
function showResults() {
    elements.resultsSection.classList.add('active');
    // Scroll to results
    elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Hide results section
 */
function hideResults() {
    elements.resultsSection.classList.remove('active');
}

/**
 * Update file name display when a file is selected
 * @param {HTMLInputElement} input - File input element
 * @param {HTMLElement} display - Element to display file name
 */
function handleFileSelect(input, display) {
    input.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            const file = this.files[0];
            display.textContent = file.name;
        } else {
            display.textContent = '';
        }
    });
}

/**
 * Populate metrics in the UI
 * @param {Object} metrics - Metrics object from API response
 */
function populateMetrics(metrics) {
    if (!metrics) {
        elements.metricSpend.textContent = '--';
        elements.metricRoas.textContent = '--';
        elements.metricCtr.textContent = '--';
        elements.metricImpressions.textContent = '--';
        return;
    }
    
    elements.metricSpend.textContent = formatCurrency(metrics.spend);
    elements.metricRoas.textContent = metrics.roas !== undefined ? metrics.roas.toFixed(2) + 'x' : '--';
    elements.metricCtr.textContent = formatPercentage(metrics.ctr);
    elements.metricImpressions.textContent = formatNumber(metrics.impressions, 0);
}

/**
 * Populate comparison section in the UI
 * @param {string} comparison - Comparison text from API response
 */
function populateComparison(comparison) {
    elements.comparisonText.textContent = comparison || 'No comparison data available';
}

/**
 * Populate guidelines list in the UI
 * @param {Array} context - Array of context chunks from API response
 */
function populateGuidelines(context) {
    // Clear existing content
    elements.guidelinesList.innerHTML = '';
    
    if (!context || context.length === 0) {
        elements.guidelinesList.innerHTML = `
            <div class="guidelines-empty">
                <svg class="guidelines-empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <p>No relevant guidelines found</p>
            </div>
        `;
        return;
    }
    
    context.forEach((chunk, index) => {
        const item = document.createElement('div');
        item.className = 'guideline-item';
        item.innerHTML = `
            <span class="guideline-index">Chunk ${index + 1}</span>
            <p class="guideline-text">${escapeHtml(chunk)}</p>
        `;
        elements.guidelinesList.appendChild(item);
    });
}

/**
 * Populate analysis section in the UI
 * @param {Object} analysis - Analysis object from API response
 */
function populateAnalysis(analysis) {
    if (!analysis) {
        elements.redFlagText.textContent = 'No analysis available';
        elements.opportunityText.textContent = 'No analysis available';
        return;
    }
    
    elements.redFlagText.textContent = analysis.red_flag || 'No red flags identified';
    elements.opportunityText.textContent = analysis.opportunity || 'No opportunities identified';
}

/**
 * Populate summary section in the UI
 * @param {string} summary - Summary text from API response
 */
function populateSummary(summary) {
    elements.summaryText.textContent = summary || 'No summary available';
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Make API call to analyze endpoint
 * @param {FormData} formData - Form data with files
 * @returns {Promise<Object>} API response
 */
async function analyzeCampaign(formData) {
    const response = await fetch(`${API_BASE_URL}${ANALYZE_ENDPOINT}`, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Server error: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
}

/**
 * Handle form submission
 * @param {Event} event - Form submit event
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    
    // Hide previous results and errors
    hideError();
    hideResults();
    
    // Validate files
    const reportFile = elements.reportFile.files[0];
    const guidelinesFile = elements.guidelinesFile.files[0];
    
    if (!reportFile) {
        showError('Please select a campaign report file (PDF or Image).');
        return;
    }
    
    if (!guidelinesFile) {
        showError('Please select a brand guidelines file (TXT).');
        return;
    }
    
    // Prepare form data
    const formData = new FormData();
    formData.append('report', reportFile);
    formData.append('guidelines', guidelinesFile);
    
    // Show loading state
    showLoading();
    
    try {
        // Make API call
        const result = await analyzeCampaign(formData);
        
        // Populate results
        populateMetrics(result.metrics);
        populateComparison(result.analysis?.comparison);
        populateGuidelines(result.context);
        populateAnalysis(result.analysis);
        populateSummary(result.analysis?.summary);
        
        // Show results
        showResults();
        
    } catch (error) {
        console.error('Analysis failed:', error);
        showError(error.message || 'An unexpected error occurred. Please try again.');
    } finally {
        hideLoading();
    }
}

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Form submission
    elements.form.addEventListener('submit', handleFormSubmit);
    
    // File input changes
    handleFileSelect(elements.reportFile, elements.reportFileName);
    handleFileSelect(elements.guidelinesFile, elements.guidelinesFileName);
    
    // Error dismiss
    elements.errorDismiss.addEventListener('click', hideError);
    
    // Close error on click outside
    elements.errorContainer.addEventListener('click', function(event) {
        if (event.target === elements.errorContainer) {
            hideError();
        }
    });
    
    // Keyboard accessibility for error dismiss
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && elements.errorContainer.classList.contains('active')) {
            hideError();
        }
    });
}

/**
 * Initialize the application
 */
function init() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initializeElements();
            initializeEventListeners();
        });
    } else {
        initializeElements();
        initializeEventListeners();
    }
}

// Start the application
init();
