import React, { useEffect, useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { ArrowUpRight, ArrowDownRight, DollarSign, Package, AlertTriangle, Layers, Gauge } from 'lucide-react';
import api from '@/lib/api';

const KPICard = ({ title, value, subtext, icon: Icon, trend, color, delay, onClick }) => (
    <Card
        onClick={onClick}
        className="relative overflow-hidden bg-white/80 border-slate-200 shadow-xl group hover:border-[#00BAC6]/50 transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
    >
        <div className={`absolute top-0 left-0 w-1 h-full ${color}`} />
        <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">{title}</p>
                </div>
                <div className={`p-2 rounded-lg ${color.replace('bg-', 'bg-opacity-10 bg-')} shadow-sm`}>
                    <Icon size={20} className={color.replace('bg-', 'text-')} />
                </div>
            </div>

            <div className="flex items-end space-x-2">
                <h3 className="text-3xl font-extrabold text-slate-900 tracking-tight">{value}</h3>
            </div>

            <div className="mt-2 flex items-center text-sm">
                {trend === 'up' ? (
                    <ArrowUpRight size={16} className="text-emerald-600 mr-1" />
                ) : (
                    <ArrowDownRight size={16} className="text-rose-600 mr-1" />
                )}
                <span className={trend === 'up' ? 'text-emerald-600 font-medium' : 'text-rose-600 font-medium'}>
                    {subtext}
                </span>
            </div>
        </CardContent>

        {/* Glow effect - subtler for light mode */}
        <div className={`absolute -bottom-6 -right-6 w-24 h-24 ${color.replace('bg-', 'bg-')} opacity-10 blur-2xl group-hover:opacity-20 transition-opacity`} />
    </Card>
);

const HeroSection = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    const scrollToSection = (id) => {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await api.get('/api/kpis');
                setData(res.data);
            } catch (error) {
                console.error("Failed to load KPIs", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 animate-pulse">
            {[1, 2, 3, 4].map(i => <div key={i} className="h-40 bg-gray-900/50 rounded-xl border border-gray-800" />)}
        </div>
    );

    if (!data) return null;

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 lg:gap-6 mb-8">
            <KPICard
                title="Revenue Protected"
                value={`₹${(data.revenue_protected / 100000).toFixed(1)}L`}
                subtext="High Impact Decisions"
                icon={DollarSign}
                trend="up"
                color="bg-[#00BAC6]"
                onClick={() => scrollToSection('insights-section')}
            />
            <KPICard
                title="Working Capital Freed"
                value={`₹${(data.working_capital_freed / 100000).toFixed(1)}L`}
                subtext="Inventory Optimized"
                icon={Layers}
                trend="up"
                color="bg-[#3BB19B]"
                onClick={() => scrollToSection('allocation-section')}
            />
            <KPICard
                title="Stock-Out Reduction"
                value={`${data.stockout_reduction_pct}%`}
                subtext="Service Level Improvement"
                icon={AlertTriangle}
                trend="up"
                color="bg-[#FFD700]"
                onClick={() => scrollToSection('risk-section')}
            />
            <KPICard
                title="Production Accuracy"
                value={`${data.production_accuracy_skus}`}
                subtext="SKU Configurations"
                icon={Package}
                trend="up"
                color="bg-[#000042]"
                onClick={() => scrollToSection('production-section')}
            />
            <KPICard
                title="Capacity Utilization"
                value={`${data.capacity_utilization_pct || 0}%`}
                subtext={data.capacity_utilization_pct > 90 ? 'Near Full Capacity' : 'Capacity Available'}
                icon={Gauge}
                trend={data.capacity_utilization_pct > 90 ? 'down' : 'up'}
                color="bg-[#8B5CF6]"
                onClick={() => scrollToSection('capacity-section')}
            />
        </div>
    );
};

export default HeroSection;
