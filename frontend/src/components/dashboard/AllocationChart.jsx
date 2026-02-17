import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import api from '@/lib/api';
import { Truck } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const AllocationChart = () => {
    const [data, setData] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await api.get('/api/allocation');
                setData(res.data.slice(0, 8)); // Top 8 cities
            } catch (error) {
                console.error("Failed to load allocation", error);
            }
        };
        fetchData();
    }, []);

    return (
        <Card className="bg-white/80 border-slate-200 shadow-xl h-full flex flex-col">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-lg font-bold text-slate-900 flex items-center">
                    <Truck className="mr-2 text-emerald-600" size={18} />
                    Inventory Allocation
                </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 min-h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
                        <XAxis type="number" stroke="#64748b" fontSize={10} hide />
                        <YAxis dataKey="city" type="category" stroke="#94a3b8" fontSize={11} width={80} tickLine={false} axisLine={false} />
                        <Tooltip
                            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }}
                        />
                        <Bar dataKey="allocated_units" fill="#10b981" radius={[0, 4, 4, 0]} barSize={20} />
                    </BarChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
};

export default AllocationChart;
