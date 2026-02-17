import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import api from '@/lib/api';
import { Lightbulb, AlertTriangle, Factory, DollarSign } from 'lucide-react';

const iconMap = {
    risk: AlertTriangle,
    production: Factory,
    revenue: DollarSign
};

const ExecutiveInsights = () => {
    const [insights, setInsights] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await api.get('/api/insights');
                setInsights(res.data);
            } catch (error) {
                console.error("Failed to load insights", error);
            }
        };
        fetchData();
    }, []);

    return (
        <Card className="bg-white/80 border-slate-200 shadow-xl">
            <CardHeader>
                <CardTitle className="flex items-center text-lg text-slate-900">
                    <Lightbulb className="mr-2 text-yellow-500" size={20} />
                    Executive Insights
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {insights.map((insight, idx) => {
                    const Icon = iconMap[insight.type] || Lightbulb;
                    return (
                        <div key={idx} className="flex items-start space-x-4 p-4 rounded-lg bg-slate-50 border border-slate-100 hover:bg-slate-100 transition-colors">
                            <div className={`p-2 rounded-lg ${insight.bg} ${insight.color}`}>
                                <Icon size={20} />
                            </div>
                            <div>
                                <p className="text-slate-600 text-sm font-medium">{insight.message}</p>
                                <p className={`text-lg font-bold ${insight.color} mt-1`}>{insight.value}</p>
                            </div>
                        </div>
                    );
                })}
            </CardContent>
        </Card>
    );
};

export default ExecutiveInsights;
