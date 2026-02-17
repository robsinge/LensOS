import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import api from '@/lib/api';
import { motion, AnimatePresence } from "framer-motion";
import { Factory, ShieldCheck } from 'lucide-react';

const ConfidenceBadge = ({ score }) => {
    const pct = (score * 100).toFixed(0);
    let color = 'bg-rose-50 text-rose-700 border-rose-200 ring-rose-500/10';

    if (score >= 0.75) {
        color = 'bg-emerald-50 text-emerald-700 border-emerald-200 ring-emerald-500/10';
    } else if (score >= 0.55) {
        color = 'bg-amber-50 text-amber-700 border-amber-200 ring-amber-500/10';
    }

    return (
        <div className="group relative flex items-center justify-end">
            <span className={`tour-confidence-badge inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-extrabold border ring-1 ${color} cursor-help transition-all duration-300 hover:scale-105 hover:shadow-sm`}>
                <ShieldCheck size={11} className="mr-1" />
                {pct}%
            </span>
            {/* Custom Tooltip */}
            <div className="invisible group-hover:visible opacity-0 group-hover:opacity-100 transition-all duration-200 absolute bottom-full right-0 mb-2 w-48 p-2.5 bg-slate-800 text-slate-100 text-[10px] leading-relaxed rounded-lg shadow-xl z-50 border border-slate-700 pointer-events-none">
                Confidence reflects forecast uncertainty based on historical variability.
                <div className="absolute top-full right-4 border-4 border-transparent border-t-slate-800" />
            </div>
        </div>
    );
};

const ProductionTable = () => {
    const [data, setData] = useState([]);
    const [confidence, setConfidence] = useState({});

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [prodRes, confRes] = await Promise.all([
                    api.get('/api/production'),
                    api.get('/api/confidence').catch(() => ({ data: [] })),
                ]);
                setData(prodRes.data.slice(0, 7)); // Top 7

                // Build lookup: sku_id+power_cluster → confidence_score
                const confMap = {};
                (confRes.data || []).forEach(item => {
                    confMap[`${item.sku_id}_${item.power_cluster}`] = item.confidence_score;
                });
                setConfidence(confMap);
            } catch (error) {
                console.error("Failed to load production plan", error);
            }
        };
        fetchData();
    }, []);

    return (
        <Card className="bg-white/80 border-slate-200 shadow-xl h-full flex flex-col">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-lg font-bold text-slate-900 flex items-center">
                    <Factory className="mr-2 text-[#00BAC6]" size={18} />
                    Top Production Recommendations
                </CardTitle>
                <Badge variant="outline" className="text-[#00BAC6] border-[#00BAC6]/30 bg-[#00BAC6]/10">
                    Week 24
                </Badge>
            </CardHeader>
            <CardContent className="flex-1 overflow-auto">
                <div className="space-y-4">
                    {/* Header Row - Hidden on Mobile */}
                    <div className="hidden md:grid grid-cols-12 text-xs font-medium text-slate-500 uppercase px-4 py-2 border-b border-slate-100">
                        <div className="col-span-3">SKU</div>
                        <div className="col-span-3">Cluster</div>
                        <div className="col-span-3 text-right">Quantity</div>
                        <div className="col-span-3 text-right">Confidence</div>
                    </div>

                    <AnimatePresence>
                        {data.map((item, index) => {
                            const confScore = confidence[`${item.sku_id}_${item.power_cluster}`];
                            return (
                                <motion.div
                                    key={`${item.sku_id}-${item.power_cluster}`}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    className="relative p-4 rounded-lg bg-slate-50 md:bg-transparent md:hover:bg-slate-50 transition-colors group border md:border-none border-slate-100 mb-2 md:mb-0"
                                >
                                    <div className="grid grid-cols-1 md:grid-cols-12 items-center gap-2 md:gap-0">
                                        {/* Mobile: SKU & Cluster Row */}
                                        <div className="col-span-1 md:col-span-3 flex justify-between md:block items-center">
                                            <span className="md:hidden text-xs text-slate-400 uppercase font-medium">SKU</span>
                                            <div className="font-mono text-sm text-[#00BAC6] font-bold md:font-normal group-hover:text-[#008f99] transition-colors">
                                                {item.sku_id}
                                            </div>
                                        </div>

                                        <div className="col-span-1 md:col-span-3 flex justify-between md:block items-center">
                                            <span className="md:hidden text-xs text-slate-400 uppercase font-medium">Cluster</span>
                                            <Badge variant="secondary" className="bg-slate-100 text-slate-600 border-slate-200">
                                                {item.power_cluster}
                                            </Badge>
                                        </div>

                                        {/* Mobile: Qty & Confidence Row */}
                                        <div className="col-span-1 md:col-span-3 flex justify-between md:block items-center md:text-right">
                                            <span className="md:hidden text-xs text-slate-400 uppercase font-medium">Qty</span>
                                            <div className="font-bold text-slate-900">
                                                {item.recommended_production_qty.toLocaleString()} <span className="text-xs text-slate-400 font-normal">units</span>
                                            </div>
                                        </div>

                                        <div className="col-span-1 md:col-span-3 flex justify-between md:block items-center md:text-right">
                                            <span className="md:hidden text-xs text-slate-400 uppercase font-medium">Conf.</span>
                                            <div className="flex justify-end w-full">
                                                {confScore !== undefined ? (
                                                    <ConfidenceBadge score={confScore} />
                                                ) : (
                                                    <span className="text-xs text-slate-300">—</span>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Progress Bar */}
                                    <div className="mt-3 md:mt-2 h-1 md:h-0.5 bg-slate-200 md:bg-slate-100 rounded-full overflow-hidden w-full">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${(item.recommended_production_qty / data[0]?.recommended_production_qty) * 100}%` }}
                                            transition={{ duration: 1, delay: 0.5 + index * 0.1 }}
                                            className="h-full bg-[#00BAC6]/70"
                                        />
                                    </div>
                                </motion.div>
                            );
                        })}
                    </AnimatePresence>
                </div>
            </CardContent>
        </Card>
    );
};

export default ProductionTable;
