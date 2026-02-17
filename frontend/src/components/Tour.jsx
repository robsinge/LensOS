import React, { useEffect, useState } from 'react';
import Joyride, { ACTIONS, EVENTS, STATUS } from 'react-joyride';

const Tour = ({ run, onFinish }) => {
    const [stepIndex, setStepIndex] = useState(0);
    const [isMobile, setIsMobile] = useState(false);

    useEffect(() => {
        const checkMobile = () => {
            setIsMobile(window.innerWidth < 1024); // lg breakpoint
        };
        checkMobile();
        window.addEventListener('resize', checkMobile);
        return () => window.removeEventListener('resize', checkMobile);
    }, []);

    const steps = [
        {
            target: 'body',
            title: 'Welcome to LensOS',
            content: (
                <div>
                    <strong className="block mb-1">What is this:</strong>
                    <p className="mb-2">Predictive supply-chain intelligence platform.</p>
                    <strong className="block mb-1">How it works:</strong>
                    <p className="mb-2">Time-series ML + optimization + decision APIs.</p>
                    <strong className="block mb-1">What it can do:</strong>
                    <p>Pre-empt demand and automate operations decisions.</p>
                </div>
            ),
            placement: 'center',
            disableBeacon: true,
        },
        {
            target: '#executive-brief',
            title: 'Executive Decision Brief',
            content: (
                <div>
                    <strong className="block mb-1">What is this:</strong>
                    <p className="mb-2">AI-generated weekly directives.</p>
                    <strong className="block mb-1">How it works:</strong>
                    <p className="mb-2">Forecast outputs → optimization engine → rule-based narrative layer.</p>
                    <strong className="block mb-1">What it can do:</strong>
                    <p>Translate models into executable business actions.</p>
                </div>
            ),
        },
        {
            target: '#overview-section', // HeroSection
            title: 'Financial Impact KPIs',
            content: (
                <div>
                    <strong className="block mb-1">What is this:</strong>
                    <p className="mb-2">Quantified economic outcomes.</p>
                    <strong className="block mb-1">How it works:</strong>
                    <p className="mb-2">Revenue risk model + cost models + capacity simulation.</p>
                    <strong className="block mb-1">What it can do:</strong>
                    <p>Measure ROI of operational decisions instantly.</p>
                </div>
            ),
        },
        {
            target: '#production-section',
            title: 'Production Recommendations',
            content: (
                <div>
                    <strong className="block mb-1">What is this:</strong>
                    <p className="mb-2">SKU-level manufacturing plan.</p>
                    <strong className="block mb-1">How it works:</strong>
                    <p className="mb-2">LightGBM demand forecast + LP/MIP capacity optimizer.</p>
                    <strong className="block mb-1">What it can do:</strong>
                    <p>Determine optimal production before orders occur.</p>
                </div>
            ),
        },
        {
            target: '.tour-confidence-badge',
            title: 'Confidence Scores',
            content: (
                <div>
                    <strong className="block mb-1">What is this:</strong>
                    <p className="mb-2">Forecast uncertainty metric.</p>
                    <strong className="block mb-1">How it works:</strong>
                    <p className="mb-2">Residual variance + prediction intervals normalization.</p>
                    <strong className="block mb-1">What it can do:</strong>
                    <p>Risk-aware decision making.</p>
                </div>
            ),
        },
        {
            target: '#capacity-section', // CapacityGauge
            title: 'Capacity Utilization',
            content: (
                <div>
                    <strong className="block mb-1">What is this:</strong>
                    <p className="mb-2">Constraint-aware production load.</p>
                    <strong className="block mb-1">How it works:</strong>
                    <p className="mb-2">Linear programming with capacity constraints.</p>
                    <strong className="block mb-1">What it can do:</strong>
                    <p>Detect bottlenecks and headroom.</p>
                </div>
            ),
        },
        {
            target: '#risk-section',
            title: 'Risk Heatmap',
            content: (
                <div>
                    <strong className="block mb-1">What is this:</strong>
                    <p className="mb-2">Inventory shortage probability map.</p>
                    <strong className="block mb-1">How it works:</strong>
                    <p className="mb-2">Demand forecast vs inventory state comparison.</p>
                    <strong className="block mb-1">What it can do:</strong>
                    <p>Identify revenue-loss zones.</p>
                </div>
            ),
        },
        {
            target: '#allocation-section',
            title: 'Inventory Allocation',
            content: (
                <div>
                    <strong className="block mb-1">What is this:</strong>
                    <p className="mb-2">Distribution optimization plan.</p>
                    <strong className="block mb-1">How it works:</strong>
                    <p className="mb-2">Proportional allocation + constraint solver.</p>
                    <strong className="block mb-1">What it can do:</strong>
                    <p>Prioritize high-demand regions.</p>
                </div>
            ),
        },
        {
            target: '#scenario-panel', // Target the panel specifically if ID exists, else parent section
            title: 'Scenario Simulator',
            content: (
                <div>
                    <strong className="block mb-1">What is this:</strong>
                    <p className="mb-2">Parametric decision engine.</p>
                    <strong className="block mb-1">How it works:</strong>
                    <p className="mb-2">Real-time recomputation with demand/price/capacity multipliers.</p>
                    <strong className="block mb-1">What it can do:</strong>
                    <p>Strategic planning under uncertainty.</p>
                </div>
            ),
        },
        {
            target: '#simulator-section', // New Product Simulator
            title: 'New Product Launch Simulator',
            content: (
                <div>
                    <strong className="block mb-1">What is this:</strong>
                    <p className="mb-2">Zero-history demand prediction.</p>
                    <strong className="block mb-1">How it works:</strong>
                    <p className="mb-2">Feature embeddings + nearest-neighbor similarity.</p>
                    <strong className="block mb-1">What it can do:</strong>
                    <p>Forecast demand pre-launch.</p>
                </div>
            ),
        },
        {
            target: '#insights-section', // Impact Comparison
            title: 'AI Impact Comparison',
            content: (
                <div>
                    <strong className="block mb-1">What is this:</strong>
                    <p className="mb-2">Baseline vs optimized performance.</p>
                    <strong className="block mb-1">How it works:</strong>
                    <p className="mb-2">Counterfactual simulation (traditional vs AI).</p>
                    <strong className="block mb-1">What it can do:</strong>
                    <p>Demonstrate efficiency gains.</p>
                </div>
            ),
        },
        {
            target: 'body',
            title: 'System Completion',
            content: (
                <div>
                    <strong className="block mb-1">What is this:</strong>
                    <p className="mb-2">Integrated intelligence stack.</p>
                    <strong className="block mb-1">How it works:</strong>
                    <p className="mb-2">Data pipeline + ML models + optimization + UI.</p>
                    <strong className="block mb-1">What it can do:</strong>
                    <p>End-to-end autonomous planning capability.</p>
                </div>
            ),
            placement: 'center',
        },
    ];

    // Mobile Optimization: Force bottom placement on mobile
    const tourSteps = steps.map(step => ({
        ...step,
        placement: isMobile && step.target !== 'body' ? 'bottom' : step.placement,
        disableBeacon: true, // cleaner look
    }));

    const handleCallback = (data) => {
        const { action, index, status, type } = data;

        if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status)) {
            setStepIndex(0);
            onFinish();
        } else if ([EVENTS.STEP_AFTER, EVENTS.TARGET_NOT_FOUND].includes(type)) {
            const nextStepIndex = index + (action === ACTIONS.PREV ? -1 : 1);

            // Manual scroll logic
            if (nextStepIndex >= 0 && nextStepIndex < steps.length) {
                const targetSelector = steps[nextStepIndex].target;
                if (targetSelector !== 'body') {
                    const element = document.querySelector(targetSelector);
                    if (element) {
                        element.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                    } else {
                        // Fallback safety
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    }
                }
            }

            // Delay for scroll to complete
            setTimeout(() => {
                setStepIndex(nextStepIndex);
            }, 400); // Increased to 400ms for safety
        }
    };

    return (
        <Joyride
            steps={tourSteps}
            run={run}
            stepIndex={stepIndex}
            continuous
            showProgress
            showSkipButton
            scrollToFirstStep={true}
            disableScrolling={false} // We handle scrolling manually
            scrollOffset={150} // Ensure header doesn't cover
            spotlightClicks={true}
            floaterProps={{
                disableAnimation: true,
            }}
            callback={handleCallback}
            styles={{
                options: {
                    primaryColor: '#00BAC6',
                    zIndex: 10000,
                },
                tooltip: {
                    fontSize: '14px',
                    borderRadius: '0.75rem',
                },
                buttonNext: {
                    backgroundColor: '#00BAC6',
                    color: '#fff',
                    fontWeight: 'bold',
                },
                buttonBack: {
                    color: '#64748b',
                },
            }}
            locale={{
                last: 'Explore Dashboard',
                skip: 'Skip Tour',
            }}
        />
    );
};

export default Tour;
