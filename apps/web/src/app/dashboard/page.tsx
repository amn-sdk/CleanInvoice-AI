'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';

interface Invoice {
    id: string;
    total_ttc: string;
    status: string;
}

interface Stats {
    total_invoices: number;
    total_revenue: number;
    pending_invoices: number;
    late_invoices: number;
}

export default function DashboardPage() {
    const [stats, setStats] = useState<Stats>({
        total_invoices: 0,
        total_revenue: 0,
        pending_invoices: 0,
        late_invoices: 0,
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await apiClient.get('/invoices/');
                const invoices = response.data;

                // Calculate basic stats
                const stats = {
                    total_invoices: invoices.length,
                    total_revenue: invoices.reduce((sum: number, inv: Invoice) => sum + parseFloat(inv.total_ttc), 0),
                    pending_invoices: invoices.filter((inv: Invoice) => inv.status === 'ISSUED').length,
                    late_invoices: invoices.filter((inv: Invoice) => inv.status === 'LATE').length,
                };

                setStats(stats);
            } catch (error) {
                console.error('Failed to fetch stats', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    const StatCard = ({ title, value, icon, color }: { title: string; value: string | number; icon: string; color: string }) => (
        <div className={`bg-white p-6 rounded-xl shadow-md border-l-4 ${color}`}>
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-gray-600 text-sm font-medium">{title}</p>
                    <p className="text-3xl font-bold mt-2">{value}</p>
                </div>
                <div className="text-4xl">{icon}</div>
            </div>
        </div>
    );

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-gray-500">Chargement...</div>
            </div>
        );
    }

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-600 mt-2">Vue d&apos;ensemble de votre activité</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Factures"
                    value={stats.total_invoices}
                    icon="📄"
                    color="border-blue-500"
                />
                <StatCard
                    title="Chiffre d'affaires"
                    value={`${stats.total_revenue.toFixed(2)} €`}
                    icon="💰"
                    color="border-green-500"
                />
                <StatCard
                    title="En attente"
                    value={stats.pending_invoices}
                    icon="⏳"
                    color="border-yellow-500"
                />
                <StatCard
                    title="En retard"
                    value={stats.late_invoices}
                    icon="⚠️"
                    color="border-red-500"
                />
            </div>

            <div className="mt-8 bg-white p-6 rounded-xl shadow-md">
                <h2 className="text-xl font-bold mb-4">Activité récente</h2>
                <div className="text-gray-500 text-center py-8">
                    Aucune activité récente
                </div>
            </div>
        </div>
    );
}
