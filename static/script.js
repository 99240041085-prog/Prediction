// ─── Slider Value Updates ──────────────────────────────────────
const sliders = [
    { id: 'ai_dependency_score', decimals: 0 },
    { id: 'ai_generated_content_percentage', decimals: 0 },
    { id: 'last_exam_score', decimals: 0 },
    { id: 'ai_usage_hours', decimals: 1 }, // NEW
    { id: 'study_consistency_index', decimals: 1 },
    { id: 'sleep_hours', decimals: 1 },
];

sliders.forEach(({ id, decimals }) => {
    const slider = document.getElementById(id);
    const display = document.getElementById(`${id}_val`);
    if (slider && display) {
        // Set initial value
        display.textContent = parseFloat(slider.value).toFixed(decimals);
        // Update on input
        slider.addEventListener('input', () => {
            display.textContent = parseFloat(slider.value).toFixed(decimals);
        });
    }
});

// ─── Form Submission ───────────────────────────────────────────
const form = document.getElementById('predictionForm');
const predictBtn = document.getElementById('predictBtn');
const btnText = predictBtn.querySelector('.btn-text');
const btnLoader = predictBtn.querySelector('.btn-loader');
const btnIcon = predictBtn.querySelector('.btn-icon');
const resultsPanel = document.getElementById('resultsPanel');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Show loading state
    btnText.textContent = 'Analyzing...';
    btnLoader.style.display = 'inline-flex';
    btnIcon.style.display = 'none';
    predictBtn.disabled = true;
    predictBtn.style.opacity = '0.8';

    // Gather form data
    const payload = {
        ai_tools_used: document.getElementById('ai_tools_used').value,
        ai_usage_purpose: document.getElementById('ai_usage_purpose').value,
        ai_dependency_score: parseFloat(document.getElementById('ai_dependency_score').value),
        ai_generated_content_percentage: parseFloat(document.getElementById('ai_generated_content_percentage').value),
        last_exam_score: parseFloat(document.getElementById('last_exam_score').value),
        ai_usage_hours: parseFloat(document.getElementById('ai_usage_hours').value), // NEW
        study_consistency_index: parseFloat(document.getElementById('study_consistency_index').value),
        sleep_hours: parseFloat(document.getElementById('sleep_hours').value),
    };

    console.log("Payload sent:", payload);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            cache: 'no-store'
        });

        const data = await response.json();
        console.log("Response received:", data);

        if (data.success) {
            displayResults(data.predictions);
        } else {
            alert('Prediction failed: ' + (data.error || 'Unknown error'));
        }
    } catch (err) {
        alert('Network error: ' + err.message);
    } finally {
        // Reset button
        btnText.textContent = 'Predict Performance';
        btnLoader.style.display = 'none';
        btnIcon.style.display = 'inline';
        predictBtn.disabled = false;
        predictBtn.style.opacity = '1';
    }
});

// ─── Display Results ───────────────────────────────────────────
function displayResults(predictions) {
    resultsPanel.style.display = 'block';

    // Scroll to results smoothly
    setTimeout(() => {
        resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);

    // ── Score WITH AI ──
    const withAi = predictions.final_score_with_ai;
    const withAiValue = document.getElementById('withAiValue');
    const withAiBar = document.getElementById('withAiBar');
    const withAiPassed = document.getElementById('withAiPassed');

    animateNumber(withAiValue, 0, withAi, 1200, 1);
    setTimeout(() => {
        withAiBar.style.width = `${Math.min(withAi, 100)}%`;
    }, 200);

    const passedWith = predictions.passed_with_ai === 'Yes';
    withAiPassed.textContent = passedWith ? '✅ Passed' : '❌ Not Passed';
    withAiPassed.className = `result-sub ${passedWith ? 'passed-yes' : 'passed-no'}`;

    // ── Last Exam Score (Reference) ──
    const lastExam = predictions.last_exam_score;

    console.log("Last Exam Score from backend:", lastExam);
    if (lastExam === undefined || lastExam === null) {
        console.warn("last exam is invalid:", lastExam);
    }

    const lastExamValue = document.getElementById('lastExamValue');
    const lastExamBar = document.getElementById('lastExamBar');

    animateNumber(lastExamValue, 0, lastExam, 1200, 1);
    setTimeout(() => {
        lastExamBar.style.width = `${Math.min(lastExam, 100)}%`;
    }, 200);

    // ── AI Impact ──
    const impact = predictions.ai_impact;
    const impactValue = document.getElementById('impactValue');
    const impactIndicator = document.getElementById('impactIndicator');
    const impactSub = document.getElementById('impactSub');

    const prefix = impact >= 0 ? '+' : '';
    animateNumber(impactValue, 0, impact, 1200, 2, prefix);

    // Impact indicator bar
    const impactAbs = Math.min(Math.abs(impact), 30);
    const impactPct = (impactAbs / 30) * 100;
    const isPositive = impact >= 0;

    impactIndicator.innerHTML = `
        <div class="impact-bar-track">
            <div class="impact-bar-fill ${isPositive ? 'impact-positive' : 'impact-negative'}" 
                 style="width: 0"></div>
        </div>
    `;

    setTimeout(() => {
        const fill = impactIndicator.querySelector('.impact-bar-fill');
        if (fill) fill.style.width = `${impactPct}%`;
    }, 400);

    if (impact > 5) {
        impactSub.textContent = '🚀 AI significantly boosts score';
        impactSub.style.color = '#22c55e';
    } else if (impact > 0) {
        impactSub.textContent = '📈 AI slightly helps';
        impactSub.style.color = '#6366f1';
    } else if (impact > -5) {
        impactSub.textContent = '⚠️ AI slightly hurts score';
        impactSub.style.color = '#f59e0b';
    } else {
        impactSub.textContent = '📉 AI significantly hurts score';
        impactSub.style.color = '#ef4444';
    }

    // Re-trigger card animations
    document.querySelectorAll('.result-card').forEach((card, i) => {
        card.style.animation = 'none';
        card.offsetHeight; // force reflow
        card.style.animation = `scaleIn 0.5s ease-out ${0.1 + i * 0.1}s both`;
    });
}

// ─── Animated Number Counter ───────────────────────────────────
function animateNumber(element, start, end, duration, decimals = 0, prefix = '') {
    if (isNaN(end)) {
        element.textContent = '--';
        return;
    }

    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = start + (end - start) * eased;

        element.textContent = `${prefix}${current.toFixed(decimals)}`;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}
