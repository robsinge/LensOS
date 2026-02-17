import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import api from '@/lib/api';
import { SlidersHorizontal, Play, Loader2, TrendingUp, TrendingDown, ArrowRight, RotateCcw } from 'lucide-react';

const ScenarioPanel = () => {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [params, setParams] = useState({
        demand_multiplier: 1.0,
        price_multiplier: 1.0,
        capacity_change_pct: 0,
    });

    const handleRun = async () => {
        setLoading(true);
        try {
            const res = await api.post('/api/scenario', params);
            setResult(res.data);
        } catch (error) {
            console.error("Scenario failed", error);
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setParams({ demand_multiplier: 1.0, price_multiplier: 1.0, capacity_change_pct: 0 });
        setResult(null);
    };

    const DeltaIndicator = ({ value, suffix = '' }) => {
        const isPositive = value > 0;
        const isZero = value === 0;
        return (
            <span className={`inline-flex items-center text-sm font-bold ${isZero ? 'text-slate-400' : isPositive ? 'text-emerald-600' : 'text-rose-600'}`}>
                {isPositive ? <TrendingUp size={14} className="mr-1" /> : !isZero && <TrendingDown size={14} className="mr-1" />}
                {isPositive ? '+' : ''}{typeof value === 'number' ? value.toLocaleString() : value}{suffix}
            </span>
        );
    };

    return (
        <Card className="bg-white/80 border-slate-200 shadow-xl overflow-hidden relative">
            <div className="absolute top-0 right-0 p-4 opacity-5">
                <SlidersHorizontal size={100} className="text-[#FFD700]" />
            </div>

            <CardHeader className="pb-2">
                <CardTitle className="flex items-center justify-between text-xl text-slate-900">
                    <div className="flex items-center">
                        <SlidersHorizontal className="mr-2 text-[#FFD700]" size={20} />
                        Scenario Simulator
                    </div>
                    {result && (
                        <button onClick={handleReset} className="text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1 transition-colors">
                            <RotateCcw size={12} /> Reset
                        </button>
                    )}
                </CardTitle>
            </CardHeader>

            <CardContent className="pt-0">
                {/* Sliders */}
                <div className="space-y-6 mb-8">
                    {/* Demand Slider */}
                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <label className="text-sm font-medium text-slate-600">Demand Change</label>
                            <span className={`text-sm font-bold ${params.demand_multiplier >= 1.0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                                {params.demand_multiplier >= 1.0 ? '+' : ''}{((params.demand_multiplier - 1) * 100).toFixed(0)}%
                            </span>
                        </div>
                        <input
                            type="range"
                            min="0.8" max="1.2" step="0.01"
                            value={params.demand_multiplier}
                            onChange={(e) => setParams({ ...params, demand_multiplier: parseFloat(e.target.value) })}
                            className="w-full h-4 md:h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#00BAC6] touch-action-manipulation"
                        />
                        <div className="flex justify-between text-xs text-slate-400 mt-1">
                            <span>-20%</span><span>0%</span><span>+20%</span>
                        </div>
                    </div>

                    {/* Price Slider */}
                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <label className="text-sm font-medium text-slate-600">Price Change</label>
                            <span className={`text-sm font-bold ${params.price_multiplier >= 1.0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                                {params.price_multiplier >= 1.0 ? '+' : ''}{((params.price_multiplier - 1) * 100).toFixed(0)}%
                            </span>
                        </div>
                        <input
                            type="range"
                            min="0.9" max="1.1" step="0.01"
                            value={params.price_multiplier}
                            onChange={(e) => setParams({ ...params, price_multiplier: parseFloat(e.target.value) })}
                            className="w-full h-4 md:h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#FFD700] touch-action-manipulation"
                        />
                        <div className="flex justify-between text-xs text-slate-400 mt-1">
                            <span>-10%</span><span>0%</span><span>+10%</span>
                        </div>
                    </div>

                    {/* Capacity Slider */}
                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <label className="text-sm font-medium text-slate-600">Capacity Change</label>
                            <span className={`text-sm font-bold ${params.capacity_change_pct >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                                {params.capacity_change_pct >= 0 ? '+' : ''}{params.capacity_change_pct}%
                            </span>
                        </div>
                        <input
                            type="range"
                            min="-20" max="20" step="1"
                            value={params.capacity_change_pct}
                            onChange={(e) => setParams({ ...params, capacity_change_pct: parseInt(e.target.value) })}
                            className="w-full h-4 md:h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#3BB19B] touch-action-manipulation"
                        />
                        <div className="flex justify-between text-xs text-slate-400 mt-1">
                            <span>-20%</span><span>0%</span><span>+20%</span>
                        </div>
                    </div>
                </div>

                {/* Run Button */}
                <Button
                    onClick={handleRun}
                    disabled={loading}
                    className="w-full h-12 text-base font-bold bg-gradient-to-r from-[#FFD700] to-[#FFA500] hover:from-[#FFA500] hover:to-[#FF8C00] text-slate-900 shadow-lg shadow-amber-200/50 transition-all active:scale-95 flex items-center justify-center mb-4"
                >
                    {loading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : <Play className="mr-2 h-5 w-5 fill-current" />}
                    {loading ? 'Computing Scenario...' : 'Run Scenario'}
                </Button>

                {/* Results */}
                {result && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-4">
                        {/* Revenue Comparison */}
                        <div className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-xl p-4 border border-slate-200">
                            <p className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-3">Revenue Impact</p>
                            <div className="flex items-center justify-between">
                                <div className="text-center">
                                    <p className="text-xs text-slate-400">Baseline</p>
                                    <p className="text-lg font-bold text-slate-700">₹{(result.baseline.total_revenue / 100000).toFixed(1)}L</p>
                                </div>
                                <ArrowRight size={20} className="text-slate-300" />
                                <div className="text-center">
                                    <p className="text-xs text-slate-400">Scenario</p>
                                    <p className="text-lg font-bold text-slate-900">₹{(result.scenario.total_revenue / 100000).toFixed(1)}L</p>
                                </div>
                                <div className="text-center bg-white rounded-lg p-2 border border-slate-200 shadow-sm">
                                    <p className="text-xs text-slate-400">Delta</p>
                                    <DeltaIndicator value={result.delta.revenue_change_pct} suffix="%" />
                                </div>
                            </div>
                        </div>

                        {/* Key Metrics */}
                        <div className="grid grid-cols-3 gap-2">
                            <div className="bg-slate-50 rounded-lg p-3 border border-slate-100 text-center">
                                <p className="text-xs text-slate-500">Demand</p>
                                <DeltaIndicator value={result.delta.demand_change} />
                            </div>
                            <div className="bg-slate-50 rounded-lg p-3 border border-slate-100 text-center">
                                <p className="text-xs text-slate-500">Production</p>
                                <DeltaIndicator value={result.delta.production_change} />
                            </div>
                            <div className="bg-slate-50 rounded-lg p-3 border border-slate-100 text-center">
                                <p className="text-xs text-slate-500">Utilization</p>
                                <p className="text-sm font-bold text-slate-700">{result.scenario.utilization_pct}%</p>
                            </div>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
};

export default ScenarioPanel;
