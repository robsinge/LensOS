import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import api from '@/lib/api';
import { AlertTriangle, Info } from 'lucide-react';
import { ResponsiveContainer, Treemap, Tooltip } from 'recharts';

const RiskHeatmap = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await api.get('/api/risk');

                // Group by Power Cluster for Treemap hierarchy
                // Data structure: name: 'root', children: [ { name: 'Cluster', children: [ { name: 'City', size: shortage } ] } ]
                const groupedMap = {};

                res.data.forEach(item => {
                    if (!groupedMap[item.power_cluster]) {
                        groupedMap[item.power_cluster] = [];
                    }
                    // Aggregate shortage by city within cluster
                    const existingCity = groupedMap[item.power_cluster].find(c => c.name === item.city);
                    if (existingCity) {
                        existingCity.size += item.shortage_units;
                    } else {
                        groupedMap[item.power_cluster].push({
                            name: item.city,
                            size: item.shortage_units,
                            risk_prob: item.risk_probability || 0.5 // Fallback if undefined
                        });
                    }
                });

                const treeData = Object.keys(groupedMap).map(cluster => ({
                    name: cluster,
                    children: groupedMap[cluster]
                }));

                setData(treeData);
            } catch (error) {
                console.error("Failed to load risk data", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const CustomContent = (props) => {
        const { root, depth, x, y, width, height, index, name, value, risk_prob } = props;

        if (depth < 2) return null; // Don't draw cluster rects if they overlap (Recharts behavior varies)

        // Color based on value (shortage) and risk probability
        // High shortage (>500) -> Dark Red
        // Med shortage (>100) -> Orange
        // Low -> Yellow
        let fill = '#fbbf24'; // Amber-400
        let textColor = '#451a03'; // Amber-950

        if (value > 1000) {
            fill = '#ef4444'; // Red-500
            textColor = '#fff';
        } else if (value > 300) {
            fill = '#f97316'; // Orange-500
            textColor = '#fff';
        }

        return (
            <g>
                <rect
                    x={x}
                    y={y}
                    width={width}
                    height={height}
                    style={{
                        fill: fill,
                        stroke: '#fff',
                        strokeWidth: 2,
                        opacity: 1,
                        transition: 'all 0.3s ease'
                    }}
                    className="hover:opacity-90 cursor-pointer"
                />
                {width > 40 && height > 30 && (
                    <>
                        <text
                            x={x + width / 2}
                            y={y + height / 2 - 6}
                            textAnchor="middle"
                            fill={textColor}
                            fontSize={11}
                            fontWeight="bold"
                            style={{ pointerEvents: 'none' }}
                        >
                            {name}
                        </text>
                        <text
                            x={x + width / 2}
                            y={y + height / 2 + 8}
                            textAnchor="middle"
                            fill={textColor}
                            fontSize={10}
                            style={{ pointerEvents: 'none', opacity: 0.9 }}
                        >
                            {value.toLocaleString()} u
                        </text>
                    </>
                )}
            </g>
        );
    };

    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl text-xs z-50">
                    <p className="font-bold text-slate-100 text-sm mb-1">{data.name}</p>
                    <div className="space-y-1">
                        <div className="flex justify-between space-x-4">
                            <span className="text-slate-400">Shortage:</span>
                            <span className="text-rose-400 font-mono font-bold">{data.size.toLocaleString()} units</span>
                        </div>
                        {/* If we had risk_prob passed down, we could show it. Recharts payload depth issues might apply. */}
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <Card className="bg-white/80 border-slate-200 shadow-xl h-full flex flex-col">
            <CardHeader className="flex flex-col md:flex-row items-start md:items-center justify-between pb-2 border-b border-slate-100 gap-2 md:gap-0">
                <CardTitle className="text-lg font-bold text-slate-900 flex items-center">
                    <AlertTriangle className="mr-2 text-rose-600" size={18} />
                    Shortage Risk Intensity
                </CardTitle>
                <div className="flex flex-wrap items-center gap-2 text-[10px] bg-slate-100 rounded-md px-2 py-1 w-full md:w-auto">
                    <div className="flex items-center"><div className="w-2 h-2 rounded-full bg-rose-500 mr-1" /> Critical</div>
                    <div className="flex items-center"><div className="w-2 h-2 rounded-full bg-orange-500 mr-1" /> Warning</div>
                    <div className="flex items-center"><div className="w-2 h-2 rounded-full bg-amber-400 mr-1" /> Monitor</div>
                </div>
            </CardHeader>
            <CardContent className="flex-1 min-h-[300px] p-0">
                <ResponsiveContainer width="100%" height="100%">
                    <Treemap
                        data={data}
                        dataKey="size"
                        aspectRatio={4 / 3}
                        stroke="#fff"
                        content={<CustomContent />}
                        animationDuration={800}
                    >
                        <Tooltip content={<CustomTooltip />} />
                    </Treemap>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
};

export default RiskHeatmap;
