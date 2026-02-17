import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import api from '@/lib/api';
import { Gauge, Factory, TrendingUp, AlertTriangle } from 'lucide-react';

const CapacityGauge = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await api.get('/api/capacity');
                setData(res.data);
            } catch (error) {
                console.error("Failed to load capacity data", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return (
        <Card className="bg-white/80 border-slate-200 shadow-xl animate-pulse">
            <CardContent className="p-6"><div className="h-64 bg-slate-100 rounded-xl" /></CardContent>
        </Card>
    );

    if (!data) return null;

    const pct = data.capacity_utilization_pct;
    const gaugeColor = pct > 90 ? '#ef4444' : pct > 70 ? '#f59e0b' : '#10b981';
    const gaugeLabel = pct > 90 ? 'Critical' : pct > 70 ? 'High Load' : 'Optimal';

    // SVG arc for the gauge
    const radius = 80;
    const circumference = Math.PI * radius; // half-circle
    const offset = circumference - (pct / 100) * circumference;

    // Calculate the additional revenue capture opportunity
    const additionalCapacity10pct = data.total_capacity * 0.10;
    const revenuePerUnit = data.revenue_captured / Math.max(data.total_optimized, 1);
    const additionalRevenue = Math.min(data.units_cut, additionalCapacity10pct) * revenuePerUnit;

    return (
        <Card className="bg-white/80 border-slate-200 shadow-xl overflow-hidden relative">
            <div className="absolute top-0 right-0 p-4 opacity-5">
                <Factory size={100} className="text-[#00BAC6]" />
            </div>

            <CardHeader className="pb-2">
                <CardTitle className="flex items-center text-xl text-slate-900">
                    <Gauge className="mr-2 text-[#00BAC6]" size={20} />
                    Capacity Utilization
                </CardTitle>
            </CardHeader>

            <CardContent className="pt-0">
                {/* Gauge */}
                <div className="flex flex-col items-center mb-6">
                    <svg width="200" height="120" viewBox="0 0 200 120" className="overflow-visible transform scale-100 md:scale-110 origin-bottom">
                        {/* Background arc */}
                        <path
                            d="M 10 110 A 80 80 0 0 1 190 110"
                            fill="none"
                            stroke="#e2e8f0"
                            strokeWidth="16"
                            strokeLinecap="round"
                        />
                        {/* Filled arc */}
                        <path
                            d="M 10 110 A 80 80 0 0 1 190 110"
                            fill="none"
                            stroke={gaugeColor}
                            strokeWidth="16"
                            strokeLinecap="round"
                            strokeDasharray={circumference}
                            strokeDashoffset={offset}
                            className="transition-all duration-1000 ease-out"
                        />
                        {/* Center text */}
                        <text x="100" y="95" textAnchor="middle" className="text-3xl font-extrabold fill-slate-900" fontSize="32">
                            {pct}%
                        </text>
                        <text x="100" y="115" textAnchor="middle" className="fill-slate-500" fontSize="12" fontWeight="500">
                            {gaugeLabel}
                        </text>
                    </svg>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-3 mb-4">
                    <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                        <p className="text-xs text-slate-500 font-medium">Optimized Output</p>
                        <p className="text-lg font-bold text-slate-900">{data.total_optimized?.toLocaleString()}</p>
                        <p className="text-xs text-slate-400">of {data.total_capacity?.toLocaleString()} cap.</p>
                    </div>
                    <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                        <p className="text-xs text-slate-500 font-medium">Units Constrained</p>
                        <p className="text-lg font-bold text-amber-600">{data.units_cut?.toLocaleString()}</p>
                        <p className="text-xs text-slate-400">demand exceeds capacity</p>
                    </div>
                    <div className="bg-emerald-50 rounded-lg p-3 border border-emerald-100">
                        <p className="text-xs text-emerald-600 font-medium">Revenue Captured</p>
                        <p className="text-lg font-bold text-emerald-700">₹{(data.revenue_captured / 100000).toFixed(1)}L</p>
                    </div>
                    <div className="bg-rose-50 rounded-lg p-3 border border-rose-100">
                        <p className="text-xs text-rose-600 font-medium">Revenue Lost</p>
                        <p className="text-lg font-bold text-rose-700">₹{(data.revenue_lost / 100000).toFixed(1)}L</p>
                    </div>
                </div>

                {/* Executive Insight */}
                {data.units_cut > 0 && (
                    <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-4">
                        <div className="flex items-start gap-2">
                            <TrendingUp size={18} className="text-amber-600 mt-0.5 shrink-0" />
                            <p className="text-sm text-amber-800">
                                <span className="font-bold">Executive Insight:</span> Increasing capacity by 10% captures an additional{' '}
                                <span className="font-bold text-amber-900">₹{(additionalRevenue / 100000).toFixed(1)}L</span> in revenue.
                            </p>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
};

export default CapacityGauge;
