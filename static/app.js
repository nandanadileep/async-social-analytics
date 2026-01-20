// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const topicInput = document.getElementById('topicInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const btnText = document.querySelector('.btn-text');
const btnLoader = document.querySelector('.btn-loader');
const retryBtn = document.getElementById('retryBtn');

const emptyState = document.getElementById('emptyState');
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const resultsSection = document.getElementById('resultsSection');

let sentimentChart = null;
let currentTopic = '';

// Event Listeners
analyzeBtn.addEventListener('click', analyzeTopic);
topicInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') analyzeTopic();
});

if (retryBtn) {
    retryBtn.addEventListener('click', () => {
        if (currentTopic) {
            topicInput.value = currentTopic;
            analyzeTopic();
        }
    });
}

// Trending pill clicks
document.querySelectorAll('.trend-pill').forEach(pill => {
    pill.addEventListener('click', () => {
        const topic = pill.getAttribute('data-topic');
        if (topic) {
            topicInput.value = topic;
            analyzeTopic();
        }
    });
});

// Main Analysis Function
async function analyzeTopic() {
    const topic = topicInput.value.trim();

    if (!topic) {
        showError('Please enter a topic to analyze');
        return;
    }

    currentTopic = topic;
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic }),
        });

        if (!response.ok) {
            throw new Error('Analysis request failed');
        }

        const data = await response.json();

        if (data.status === 'cached') {
            displayResults(data.result, topic, true);
        } else {
            await pollForResults(topic);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to analyze topic. Please try again.');
    }
}

// Poll for results
async function pollForResults(topic) {
    const maxAttempts = 20;
    const pollInterval = 1000;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        await new Promise(resolve => setTimeout(resolve, pollInterval));

        try {
            const response = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic }),
            });

            const data = await response.json();

            if (data.status === 'cached') {
                displayResults(data.result, topic, false);
                return;
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }

    showError('Analysis is taking longer than expected. Please try again.');
}

// Display Results
function displayResults(result, topic, isCached) {
    hideAllStates();
    resultsSection.style.display = 'block';

    const sentiment = result.sentiment;
    const total = result.total_posts;

    // Update metrics
    document.getElementById('totalPosts').textContent = total.toLocaleString();

    const positivePercent = ((sentiment.positive / total) * 100).toFixed(1);
    const neutralPercent = ((sentiment.neutral / total) * 100).toFixed(1);
    const negativePercent = ((sentiment.negative / total) * 100).toFixed(1);

    document.getElementById('positivePercent').textContent = `${positivePercent}%`;
    document.getElementById('neutralPercent').textContent = `${neutralPercent}%`;
    document.getElementById('negativePercent').textContent = `${negativePercent}%`;

    // Render visualizations
    renderSentimentChart(sentiment);
    renderWordCloud(result.top_words);
    renderKeywordsTable(result.top_words, total);

    // Reset button
    analyzeBtn.disabled = false;
    btnText.style.display = 'inline';
    btnLoader.style.display = 'none';
}

// Render Sentiment Chart
function renderSentimentChart(sentiment) {
    const ctx = document.getElementById('sentimentChart');

    if (sentimentChart) {
        sentimentChart.destroy();
    }

    sentimentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [sentiment.positive, sentiment.neutral, sentiment.negative],
                backgroundColor: [
                    '#00BA7C',
                    '#536471',
                    '#F91880'
                ],
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 16,
                        font: {
                            size: 12,
                            family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif',
                            weight: 600
                        },
                        color: '#E7E9EA',
                        usePointStyle: true,
                        pointStyle: 'circle',
                        boxWidth: 8,
                        boxHeight: 8
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    padding: 12,
                    titleFont: {
                        size: 13,
                        weight: 700
                    },
                    bodyFont: {
                        size: 12
                    },
                    borderColor: '#2F3336',
                    borderWidth: 1,
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${percentage}%`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

// Render Word Cloud
function renderWordCloud(topWords) {
    const wordCloud = document.getElementById('wordCloud');
    wordCloud.innerHTML = '';

    if (!topWords || topWords.length === 0) {
        wordCloud.innerHTML = '<p style="color: var(--text-secondary);">No keywords found</p>';
        return;
    }

    const maxFreq = topWords[0][1];
    const minSize = 14;
    const maxSize = 56;

    // Show top 20 words
    topWords.slice(0, 20).forEach(([word, freq], index) => {
        const size = minSize + ((freq / maxFreq) * (maxSize - minSize));

        const wordItem = document.createElement('span');
        wordItem.className = 'word-item';
        wordItem.textContent = word;
        wordItem.style.fontSize = `${size}px`;
        wordItem.style.animationDelay = `${index * 0.02}s`;
        wordItem.title = `${word}: ${freq} occurrences`;

        // Color based on rank
        if (index === 0) {
            wordItem.style.color = '#E7E9EA';
        } else if (index < 3) {
            wordItem.style.color = '#1D9BF0';
        } else if (index < 6) {
            wordItem.style.color = '#00BA7C';
        } else {
            wordItem.style.color = '#71767B';
        }

        wordCloud.appendChild(wordItem);
    });
}

// Render Keywords Table
function renderKeywordsTable(topWords, totalPosts) {
    const tbody = document.getElementById('keywordsTableBody');
    tbody.innerHTML = '';

    if (!topWords || topWords.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-secondary);">No keywords found</td></tr>';
        return;
    }

    // Show top 10 keywords
    topWords.slice(0, 10).forEach(([word, freq], index) => {
        // Mock sentiment score (0-100)
        const sentimentScore = (50 + Math.random() * 50).toFixed(3);

        // Mock trend
        const trendValue = Math.random();
        let trendClass, trendIcon, trendColor;

        if (trendValue > 0.6) {
            trendClass = 'up';
            trendIcon = '▲';
            trendColor = '#00BA7C';
        } else if (trendValue < 0.4) {
            trendClass = 'down';
            trendIcon = '▼';
            trendColor = '#F91880';
        } else {
            trendClass = 'neutral';
            trendIcon = '—';
            trendColor = '#536471';
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="rank-number">${index + 1}.</span></td>
            <td><span class="keyword-text">${word}</span></td>
            <td>${freq.toLocaleString()}</td>
            <td><span class="sentiment-score">${sentimentScore}</span></td>
            <td>
                <span class="trend-indicator ${trendClass}">
                    ${trendIcon}
                    <span style="width: 12px; height: 12px; background: ${trendColor}; border-radius: 50%; display: inline-block;"></span>
                </span>
            </td>
        `;

        tbody.appendChild(row);
    });
}

// State Management
function showLoading() {
    hideAllStates();
    loadingState.style.display = 'block';
    analyzeBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
}

function showError(message) {
    hideAllStates();
    errorState.style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
    analyzeBtn.disabled = false;
    btnText.style.display = 'inline';
    btnLoader.style.display = 'none';
}

function hideAllStates() {
    emptyState.style.display = 'none';
    loadingState.style.display = 'none';
    errorState.style.display = 'none';
    resultsSection.style.display = 'none';
}
