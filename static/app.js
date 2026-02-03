// AI Farming Advisor - Frontend JavaScript

class FarmingAdvisorUI {
    constructor() {
        // Detect if running on Vercel or local
        this.apiBaseUrl = window.location.hostname.includes('vercel.app') ? '/api' : '';
        this.currentLocation = null;
        this.init();
    }

    init() {
        // Initialize event listeners
        this.setupEventListeners();
        
        // Load sample coordinates for demo
        this.loadSampleLocation();
    }

    setupEventListeners() {
        // Form submission
        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && (e.target.id === 'latitude' || e.target.id === 'longitude')) {
                this.getRecommendations();
            }
        });

        // Modal close on outside click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });
    }

    loadSampleLocation() {
        // Load Iowa, USA as default (good agricultural region)
        document.getElementById('latitude').value = '42.0';
        document.getElementById('longitude').value = '-93.5';
    }

    async lookupLocation() {
        const latitude = parseFloat(document.getElementById('latitude').value);
        const longitude = parseFloat(document.getElementById('longitude').value);

        if (!this.validateCoordinates(latitude, longitude)) {
            return;
        }

        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner"></span> Looking up...';
        button.disabled = true;

        try {
            const response = await fetch(`${this.apiBaseUrl}/location/${latitude}/${longitude}`);
            
            if (response.ok) {
                const locationData = await response.json();
                this.showSuccess(`📍 Location: ${locationData.location_name}`);
            } else {
                this.showError('Unable to lookup location name.');
            }

        } catch (error) {
            this.showError('Location lookup failed. Please check your internet connection.');
        } finally {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }

    async getCurrentLocation() {
        if (!navigator.geolocation) {
            this.showError('Geolocation is not supported by this browser.');
            return;
        }

        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner"></span> Getting location...';
        button.disabled = true;

        try {
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000 // 5 minutes
                });
            });

            const lat = position.coords.latitude.toFixed(4);
            const lon = position.coords.longitude.toFixed(4);

            document.getElementById('latitude').value = lat;
            document.getElementById('longitude').value = lon;

            // Get and display place name
            try {
                const locationResponse = await fetch(`${this.apiBaseUrl}/location/${lat}/${lon}`);
                if (locationResponse.ok) {
                    const locationData = await locationResponse.json();
                    this.showSuccess(`Location detected: ${locationData.location_name}`);
                } else {
                    this.showSuccess('Location detected successfully!');
                }
            } catch (e) {
                this.showSuccess('Location detected successfully!');
            }

        } catch (error) {
            let message = 'Unable to get your location. ';
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    message += 'Please allow location access and try again.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    message += 'Location information is unavailable.';
                    break;
                case error.TIMEOUT:
                    message += 'Location request timed out.';
                    break;
                default:
                    message += 'An unknown error occurred.';
                    break;
            }
            this.showError(message);
        } finally {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }

    async getRecommendations() {
        const latitude = parseFloat(document.getElementById('latitude').value);
        const longitude = parseFloat(document.getElementById('longitude').value);
        const analysisType = document.querySelector('input[name="analysisType"]:checked').value;

        // Validation
        if (!this.validateCoordinates(latitude, longitude)) {
            return;
        }

        // Show loading state
        this.setLoadingState(true);
        this.hideError();
        this.hideResults();

        try {
            let result;
            const startTime = Date.now();

            switch (analysisType) {
                case 'quick':
                    result = await this.getQuickRecommendations(latitude, longitude);
                    break;
                case 'comprehensive':
                    result = await this.getComprehensiveAnalysis(latitude, longitude);
                    break;
                case 'ndvi':
                    result = await this.getNDVIAnalysis(latitude, longitude);
                    break;
            }

            const responseTime = Date.now() - startTime;
            this.displayResults(result, analysisType, responseTime);

        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(`Analysis failed: ${error.message}`);
        } finally {
            this.setLoadingState(false);
        }
    }

    validateCoordinates(lat, lon) {
        if (isNaN(lat) || isNaN(lon)) {
            this.showError('Please enter valid latitude and longitude coordinates.');
            return false;
        }

        if (lat < -90 || lat > 90) {
            this.showError('Latitude must be between -90 and 90 degrees.');
            return false;
        }

        if (lon < -180 || lon > 180) {
            this.showError('Longitude must be between -180 and 180 degrees.');
            return false;
        }

        return true;
    }

    async getQuickRecommendations(latitude, longitude) {
        const response = await fetch(`${this.apiBaseUrl}/recommendations/quick`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ latitude, longitude })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    async getComprehensiveAnalysis(latitude, longitude) {
        const response = await fetch(`${this.apiBaseUrl}/recommendations/comprehensive?max_crops=5&detailed_explanations=true`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                latitude, 
                longitude
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    async getNDVIAnalysis(latitude, longitude) {
        const response = await fetch(`${this.apiBaseUrl}/ndvi/${latitude}/${longitude}?days_back=30`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    displayResults(data, analysisType, responseTime) {
        const resultsSection = document.getElementById('resultsSection');
        const resultsTitle = document.getElementById('resultsTitle');
        const resultsMeta = document.getElementById('resultsMeta');
        const resultsContent = document.getElementById('resultsContent');

        // Set title and metadata
        const titles = {
            'quick': '⚡ Quick Analysis Results',
            'comprehensive': '🔬 Comprehensive Analysis Results',
            'ndvi': '🛰️ Satellite Analysis Results'
        };

        resultsTitle.textContent = titles[analysisType];
        
        // Enhanced metadata with location name
        const locationDisplay = data.location_details?.city && data.location_details?.state 
            ? `${data.location_details.city}, ${data.location_details.state}`
            : data.location || `${data.ndvi_analysis?.location?.latitude}, ${data.ndvi_analysis?.location?.longitude}`;
            
        resultsMeta.innerHTML = `
            <div>Analysis completed in ${responseTime}ms</div>
            <div>📍 Location: ${locationDisplay}</div>
        `;

        // Display results based on type
        switch (analysisType) {
            case 'quick':
                this.displayQuickResults(resultsContent, data);
                break;
            case 'comprehensive':
                this.displayComprehensiveResults(resultsContent, data);
                break;
            case 'ndvi':
                this.displayNDVIResults(resultsContent, data);
                break;
        }

        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    displayQuickResults(container, data) {
        if (!data.top_recommendations || data.top_recommendations.length === 0) {
            container.innerHTML = '<p>No crop recommendations available for this location.</p>';
            return;
        }

        const html = `
            <div class="crop-recommendations">
                ${data.top_recommendations.map((crop, index) => `
                    <div class="crop-card">
                        <div class="crop-header">
                            <div class="crop-name">${index + 1}. ${crop.crop}</div>
                            <div class="crop-grade grade-${crop.grade}">Grade ${crop.grade}</div>
                        </div>
                        <div class="crop-details">
                            <div class="detail-item">
                                <div class="detail-label">Suitability Score</div>
                                <div class="detail-value">${crop.score?.toFixed(2) || 'N/A'}</div>
                            </div>
                        </div>
                        <div class="crop-advice">
                            ${this.formatAdvice(crop.simple_advice)}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        container.innerHTML = html;
    }

    displayComprehensiveResults(container, data) {
        const crops = data.crop_recommendations?.rule_based || [];
        const yieldPredictions = data.crop_recommendations?.yield_predictions || {};
        const ndviSummary = data.explanations?.ndvi_summary || '';
        const overallSummary = data.explanations?.overall_summary || '';

        let html = '';

        // NDVI Summary (if available)
        if (ndviSummary) {
            html += `
                <div class="ndvi-summary">
                    <h3>🛰️ Satellite Vegetation Analysis</h3>
                    <div>${this.formatText(ndviSummary)}</div>
                </div>
            `;
        }

        // Environmental Conditions
        if (data.environmental_conditions) {
            const weather = data.environmental_conditions.current_weather;
            const soil = data.environmental_conditions.soil_analysis;
            const location = data.location;
            
            html += `
                <div class="environmental-summary">
                    <h3>🌍 Environmental Conditions</h3>
                    ${location?.place_name ? `<p><strong>📍 Location:</strong> ${location.place_name}</p>` : ''}
                    <div class="crop-details">
                        <div class="detail-item">
                            <div class="detail-label">Temperature</div>
                            <div class="detail-value">${weather?.temperature}°C</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Humidity</div>
                            <div class="detail-value">${weather?.humidity}%</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Soil Type</div>
                            <div class="detail-value">${soil?.primary_soil_type}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Soil pH</div>
                            <div class="detail-value">${soil?.ph_range?.[0]?.toFixed(1)}-${soil?.ph_range?.[1]?.toFixed(1)}</div>
                        </div>
                    </div>
                </div>
            `;
        }

        // Crop Recommendations
        if (crops.length > 0) {
            html += `
                <h3>🌾 Top Crop Recommendations</h3>
                <div class="crop-recommendations">
                    ${crops.slice(0, 5).map((crop, index) => {
                        const yieldPred = yieldPredictions[crop.crop_name];
                        return `
                            <div class="crop-card">
                                <div class="crop-header">
                                    <div class="crop-name">${index + 1}. ${crop.crop_info.name}</div>
                                    <div class="crop-grade grade-${crop.suitability_score.grade}">Grade ${crop.suitability_score.grade}</div>
                                </div>
                                <div class="crop-details">
                                    <div class="detail-item">
                                        <div class="detail-label">Suitability Score</div>
                                        <div class="detail-value">${crop.suitability_score.overall_score.toFixed(2)}</div>
                                    </div>
                                    <div class="detail-item">
                                        <div class="detail-label">Temperature Match</div>
                                        <div class="detail-value">${(crop.suitability_score.temperature * 100).toFixed(0)}%</div>
                                    </div>
                                    <div class="detail-item">
                                        <div class="detail-label">Soil Match</div>
                                        <div class="detail-value">${(crop.suitability_score.soil * 100).toFixed(0)}%</div>
                                    </div>
                                    ${yieldPred ? `
                                        <div class="detail-item">
                                            <div class="detail-label">Expected Yield</div>
                                            <div class="detail-value">${this.formatNumber(yieldPred.predicted_yield_kg_per_hectare)} kg/ha</div>
                                        </div>
                                    ` : ''}
                                </div>
                                ${crop.recommendations && crop.recommendations.length > 0 ? `
                                    <div class="crop-advice">
                                        <strong>Recommendations:</strong>
                                        <ul>
                                            ${crop.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                                        </ul>
                                    </div>
                                ` : ''}
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
        }

        // Overall Summary
        if (overallSummary) {
            html += `
                <div class="overall-summary">
                    <h3>📋 Summary</h3>
                    <div>${this.formatText(overallSummary)}</div>
                </div>
            `;
        }

        container.innerHTML = html;
    }

    displayNDVIResults(container, data) {
        const ndviData = data.ndvi_analysis?.ndvi_analysis;
        const farmerSummary = data.farmer_summary;
        const alerts = data.ndvi_analysis?.alerts || [];

        if (!ndviData) {
            container.innerHTML = '<p>NDVI data not available for this location.</p>';
            return;
        }

        const html = `
            <div class="ndvi-summary">
                <h3>🛰️ Vegetation Health Analysis</h3>
                <div>${this.formatText(farmerSummary)}</div>
                
                <div class="ndvi-metrics">
                    <div class="ndvi-metric">
                        <div class="metric-value">${ndviData.current_ndvi.toFixed(3)}</div>
                        <div class="metric-label">Current NDVI</div>
                    </div>
                    <div class="ndvi-metric">
                        <div class="metric-value">${ndviData.average_ndvi.toFixed(3)}</div>
                        <div class="metric-label">Average NDVI</div>
                    </div>
                    <div class="ndvi-metric">
                        <div class="metric-value">${ndviData.trend > 0 ? '+' : ''}${ndviData.trend.toFixed(3)}</div>
                        <div class="metric-label">Trend</div>
                    </div>
                    <div class="ndvi-metric">
                        <div class="metric-value">${ndviData.health_status}</div>
                        <div class="metric-label">Health Status</div>
                    </div>
                    <div class="ndvi-metric">
                        <div class="metric-value">${ndviData.risk_level}</div>
                        <div class="metric-label">Risk Level</div>
                    </div>
                </div>
            </div>

            ${alerts.length > 0 ? `
                <div class="alerts-section">
                    <h3>⚠️ Alerts & Recommendations</h3>
                    ${alerts.map(alert => `
                        <div class="crop-advice">
                            <strong>${alert.type.replace('_', ' ').toUpperCase()}:</strong>
                            <p>${alert.message}</p>
                            <p><em>Recommendation: ${alert.recommendation}</em></p>
                        </div>
                    `).join('')}
                </div>
            ` : ''}

            <div class="ndvi-explanation">
                <h3>📖 Understanding NDVI</h3>
                <p><strong>NDVI (Normalized Difference Vegetation Index)</strong> measures vegetation health using satellite imagery:</p>
                <ul>
                    <li><strong>0.8-1.0:</strong> Very healthy, dense vegetation</li>
                    <li><strong>0.6-0.8:</strong> Healthy vegetation</li>
                    <li><strong>0.4-0.6:</strong> Moderate vegetation</li>
                    <li><strong>0.2-0.4:</strong> Sparse vegetation</li>
                    <li><strong>0.0-0.2:</strong> Bare soil or water</li>
                </ul>
            </div>
        `;

        container.innerHTML = html;
    }

    formatAdvice(advice) {
        if (!advice) return '';
        
        // Convert simple advice to HTML
        return advice.replace(/\n/g, '<br>');
    }

    formatText(text) {
        if (!text) return '';
        
        // Convert markdown-like formatting to HTML
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/•/g, '&bull;');
    }

    formatNumber(num) {
        if (!num) return 'N/A';
        return new Intl.NumberFormat().format(Math.round(num));
    }

    setLoadingState(loading) {
        const button = document.querySelector('.btn-primary');
        const btnText = button.querySelector('.btn-text');
        const btnLoading = button.querySelector('.btn-loading');

        if (loading) {
            btnText.style.display = 'none';
            btnLoading.style.display = 'flex';
            button.disabled = true;
        } else {
            btnText.style.display = 'block';
            btnLoading.style.display = 'none';
            button.disabled = false;
        }
    }

    showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorSection.style.display = 'block';
        errorSection.scrollIntoView({ behavior: 'smooth' });
    }

    hideError() {
        document.getElementById('errorSection').style.display = 'none';
    }

    showResults() {
        document.getElementById('resultsSection').style.display = 'block';
    }

    hideResults() {
        document.getElementById('resultsSection').style.display = 'none';
    }

    showSuccess(message) {
        // Simple success notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--success-color);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: var(--shadow);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    showOdishaLocations() {
        document.getElementById('odishaModal').style.display = 'flex';
    }

    setLocation(lat, lon, locationName) {
        document.getElementById('latitude').value = lat.toFixed(4);
        document.getElementById('longitude').value = lon.toFixed(4);
        this.hideModal('odishaModal');
        this.showSuccess(`📍 Location set: ${locationName} (${lat.toFixed(4)}, ${lon.toFixed(4)})`);
    }

    hideModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }
}

// Global functions for HTML onclick handlers
function getCurrentLocation() {
    window.farmingUI.getCurrentLocation();
}

function lookupLocation() {
    window.farmingUI.lookupLocation();
}

function getRecommendations() {
    window.farmingUI.getRecommendations();
}

function hideError() {
    window.farmingUI.hideError();
}

function showAbout() {
    document.getElementById('aboutModal').style.display = 'flex';
}

function showHelp() {
    document.getElementById('helpModal').style.display = 'flex';
}

function showOdishaLocations() {
    window.farmingUI.showOdishaLocations();
}

function setLocation(lat, lon, locationName) {
    window.farmingUI.setLocation(lat, lon, locationName);
}

function hideModal(modalId) {
    window.farmingUI.hideModal(modalId);
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.farmingUI = new FarmingAdvisorUI();
});