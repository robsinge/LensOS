import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Check, X } from 'lucide-react';

const ComparisonRow = ({ label, oldVal, newVal }) => (
    <div className="grid grid-cols-3 gap-4 py-4 border-b border-slate-100 last:border-0 hover:bg-slate-50 px-2 rounded-lg transition-colors">
        <div className="font-medium text-slate-700 flex items-center">{label}</div>
        <div className="text-rose-600 flex items-center text-sm">
            <X size={14} className="mr-2" />
            {oldVal}
        </div>
        <div className="text-emerald-600 flex items-center font-bold text-sm">
            <Check size={14} className="mr-2" />
            {newVal}
        </div>
    </div>
);

const BeforeAfterComparison = () => {
    return (
        <Card className="bg-white/80 border-slate-200 shadow-xl h-full">
            <CardHeader>
                <CardTitle className="text-lg text-slate-900">Traditional vs LensOS</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-3 gap-4 mb-4 text-xs font-bold text-slate-400 uppercase tracking-wider px-2">
                    <div>Metric</div>
                    <div>Traditional</div>
                    <div className="text-[#00BAC6]">LensOS AI</div>
                </div>
                <ComparisonRow
                    label="Production Strategy"
                    oldVal="Reactive / Manual"
                    newVal="Predictive / Automated"
                />
                <ComparisonRow
                    label="Forecasting Level"
                    oldVal="Aggregate / Averages"
                    newVal="SKU-Level / Granular"
                />
                <ComparisonRow
                    label="Stock-Out Risk"
                    oldVal="High (Reactive)"
                    newVal="Minimised (Proactive)"
                />
                <ComparisonRow
                    label="New Product Launch"
                    oldVal="Guesswork"
                    newVal="Similarity AI Model"
                />
            </CardContent>
        </Card>
    );
};

export default BeforeAfterComparison;
