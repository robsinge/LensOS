import React, { useState, useEffect } from 'react';
import Layout from './components/Layout'
import HeroSection from './components/dashboard/HeroSection'
import ExecutiveBrief from './components/dashboard/ExecutiveBrief'
import ProductionTable from './components/dashboard/ProductionTable'
import RiskHeadmap from './components/dashboard/RiskHeatmap'
import Simulator from './components/dashboard/Simulator'
import AllocationChart from './components/dashboard/AllocationChart'
import ExecutiveInsights from './components/dashboard/ExecutiveInsights'
import ImpactComparison from './components/dashboard/ImpactComparison'
import CapacityGauge from './components/dashboard/CapacityGauge'
import ScenarioPanel from './components/dashboard/ScenarioPanel'
import Tour from './components/Tour'
import { Button } from './components/ui/button'
import { Zap } from 'lucide-react'

function App() {
    const [runTour, setRunTour] = useState(false);

    useEffect(() => {
        // Auto-start tour if not completed
        const tourCompleted = localStorage.getItem('lensos_tour_completed');
        if (!tourCompleted) {
            setRunTour(true);
        }
    }, []);

    const handleTourFinish = () => {
        setRunTour(false);
        localStorage.setItem('lensos_tour_completed', 'true');
    };

    const handleStartTour = () => {
        setRunTour(true);
    };

    return (
        <Layout onStartTour={handleStartTour} isTourRunning={runTour}>
            <Tour run={runTour} onFinish={handleTourFinish} />

            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                        LensOS <span className="text-[#00BAC6]">Predict</span>
                    </h1>
                    <p className="text-slate-400 mt-2 text-lg">AI-Optimized Decisions for Week 24</p>
                </div>
                <div className="flex space-x-4">
                    {/* Export button removed as per request */}
                </div>
            </div>

            {/* Executive Briefing Layer */}
            <div className="animate-in fade-in slide-in-from-top-4 duration-700 delay-100" id="executive-brief">
                <ExecutiveBrief />
            </div>

            {/* Hero Section */}
            <div className="animate-in fade-in slide-in-from-top-4 duration-700" id="overview-section">
                <HeroSection />
            </div>

            {/* Main Grid: Production & Risk */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-100">
                <div className="lg:col-span-2 min-h-[500px]" id="production-section">
                    <ProductionTable />
                </div>
                <div className="min-h-[400px] lg:h-[500px]" id="risk-section">
                    <RiskHeadmap />
                </div>
            </div>

            {/* Capacity & Scenario Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-150">
                <div id="capacity-section">
                    <CapacityGauge />
                </div>
                <div id="scenario-panel">
                    <ScenarioPanel />
                </div>
            </div>

            {/* Simulator & Allocation */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200">
                <div className="lg:col-span-1" id="simulator-section">
                    <Simulator />
                </div>
                <div className="lg:col-span-1 min-h-[400px] lg:h-full" id="allocation-section">
                    <AllocationChart />
                </div>
            </div>

            {/* Footer Grid: Insights & Comparison */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300" id="insights-section">
                <ExecutiveInsights />
                <ImpactComparison />
            </div>

        </Layout>
    )
}

export default App
