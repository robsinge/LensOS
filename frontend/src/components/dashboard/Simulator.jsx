import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import api from '@/lib/api';
import { Zap, Loader2, RefreshCw } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const Simulator = () => {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [formData, setFormData] = useState({
        frame_type: 'full-rim',
        lens_type: 'single vision',
        price_band: 'mid'
    });

    const handlePredict = async () => {
        setLoading(true);
        try {
            const res = await api.post('/api/predict', formData);
            setResult(res.data);
        } catch (error) {
            console.error("Prediction failed", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Card className="bg-white/80 border-slate-200 shadow-xl overflow-hidden relative">
            <div className="absolute top-0 right-0 p-4 opacity-5">
                <Zap size={100} className="text-[#00BAC6]" />
            </div>

            <CardHeader>
                <CardTitle className="flex items-center text-xl text-slate-900">
                    <Zap className="mr-2 text-[#FFD700]" size={20} />
                    New Product Launch Simulator
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Controls */}
                    <div className="space-y-6">
                        <div className="space-y-4 bg-slate-50 p-6 rounded-xl border border-slate-200">
                            <div>
                                <label className="text-sm font-medium text-slate-600 block mb-2">Frame Type</label>
                                <div className="flex flex-wrap gap-2">
                                    {['full-rim', 'half-rim', 'rimless'].map(type => (
                                        <button
                                            key={type}
                                            onClick={() => setFormData({ ...formData, frame_type: type })}
                                            className={`px-3 py-1.5 rounded-md text-sm border transition-all ${formData.frame_type === type
                                                ? 'bg-[#00BAC6] border-[#00BAC6] text-white shadow-md'
                                                : 'bg-white border-slate-200 text-slate-600 hover:border-[#00BAC6]/50 hover:bg-slate-50'
                                                }`}
                                        >
                                            {type}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <label className="text-sm font-medium text-slate-600 block mb-2">Lens Type</label>
                                <select
                                    className="w-full bg-white border border-slate-200 text-slate-900 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-[#00BAC6] outline-none shadow-sm appearance-none"
                                    value={formData.lens_type}
                                    onChange={(e) => setFormData({ ...formData, lens_type: e.target.value })}
                                >
                                    <option value="single vision">Single Vision</option>
                                    <option value="progressive">Progressive</option>
                                    <option value="blue cut">Blue Cut</option>
                                </select>
                            </div>

                            <div>
                                <label className="text-sm font-medium text-slate-600 block mb-2">Price Band</label>
                                <div className="flex flex-wrap gap-2">
                                    {['low', 'mid', 'high', 'premium'].map(band => (
                                        <button
                                            key={band}
                                            onClick={() => setFormData({ ...formData, price_band: band })}
                                            className={`flex-1 min-w-[70px] py-2 px-3 rounded-lg text-xs font-bold uppercase transition-all border shadow-sm ${formData.price_band === band
                                                ? 'bg-[#00BAC6] border-[#00BAC6] text-white shadow-md transform scale-105'
                                                : 'bg-white border-slate-200 text-slate-500 hover:border-[#00BAC6]/50 hover:bg-slate-50'
                                                }`}
                                        >
                                            {band}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <Button
                                onClick={handlePredict}
                                disabled={loading}
                                className="w-full h-12 text-base font-bold bg-gradient-to-r from-[#00BAC6] to-[#008f99] hover:from-[#008f99] hover:to-[#007cd6] text-white shadow-lg shadow-[#00BAC6]/20 transition-all active:scale-95 flex items-center justify-center"
                            >
                                {loading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : <Zap className="mr-2 h-5 w-5 fill-current" />}
                                {loading ? 'Computing...' : 'Predict Demand'}
                            </Button>
                        </div>
                    </div>

                    {/* Results */}
                    <div className="md:col-span-2 space-y-6">
                        {!result ? (
                            <div className="h-full flex flex-col items-center justify-center text-slate-500 min-h-[300px] border-2 border-dashed border-slate-800 rounded-xl bg-slate-900/20">
                                <Zap size={48} className="mb-4 opacity-20" />
                                <p>Select attributes and click Predict to see AI forecast</p>
                            </div>
                        ) : (
                            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-6">
                                {/* KPIs */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-slate-900/80 p-5 rounded-xl border-l-4 border-blue-500 backdrop-blur-sm">
                                        <p className="text-slate-400 text-xs uppercase font-bold">Total Forecasted Demand</p>
                                        <p className="text-3xl font-bold text-white mt-1">{result.total_demand.toFixed(0)} <span className="text-sm font-normal text-slate-500">units</span></p>
                                    </div>
                                    <div className="bg-slate-900/80 p-5 rounded-xl border-l-4 border-emerald-500 backdrop-blur-sm">
                                        <p className="text-slate-400 text-xs uppercase font-bold">Top Market</p>
                                        <p className="text-xl font-bold text-white mt-1">
                                            {result.breakdown_by_city[0]?.city || 'N/A'}
                                        </p>
                                        <p className="text-sm text-emerald-400">{result.breakdown_by_city[0]?.predicted_demand.toFixed(0)} units</p>
                                    </div>
                                </div>

                                {/* Chart */}
                                <div className="h-64 bg-slate-900/30 rounded-xl p-4 border border-slate-800">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={result.breakdown_by_city.slice(0, 8)}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} vertical={false} />
                                            <XAxis dataKey="city" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                                            <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                                            <Tooltip
                                                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }}
                                            />
                                            <Bar dataKey="predicted_demand" radius={[4, 4, 0, 0]}>
                                                {result.breakdown_by_city.slice(0, 8).map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={`hsl(${210 + index * 10}, 80%, 60%)`} />
                                                ))}
                                            </Bar>
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>

                                {/* Similar SKUs */}
                                <div>
                                    <p className="text-sm font-medium text-slate-400 mb-2">Based on similarity to:</p>
                                    <div className="flex flex-wrap gap-2">
                                        {result.similar_skus.map((sku) => (
                                            <Badge key={sku.sku_id} variant="outline" className="text-xs bg-slate-900/50 border-slate-700 text-slate-300">
                                                {sku.sku_id} ({(100 - sku.similarity_distance * 100).toFixed(0)}% match)
                                            </Badge>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default Simulator;
