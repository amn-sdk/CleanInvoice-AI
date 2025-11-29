'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';

interface Invoice {
    id: string;
    type: string;
    status: string;
    number: string;
    date_issued: string;
    date_due: string;
    total_ttc: number;
}

export default function InvoicesPage() {
    const [invoices, setInvoices] = useState<Invoice[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<string>('all');

    useEffect(() => {
        const fetchInvoices = async () => {
            try {
                const response = await apiClient.get('/invoices/');
                setInvoices(response.data);
            } catch (error) {
                console.error('Failed to fetch invoices', error);
            } finally {
                setLoading(false);
            }
        };

        fetchInvoices();
    }, []);

    const filteredInvoices = invoices.filter((inv) => {
        if (filter === 'all') return true;
        return inv.status.toLowerCase() === filter.toLowerCase();
    });

    const getStatusBadge = (status: string) => {
        const styles: any = {
            DRAFT: 'bg-gray-100 text-gray-700',
            ISSUED: 'bg-blue-100 text-blue-700',
            PAID: 'bg-green-100 text-green-700',
            LATE: 'bg-red-100 text-red-700',
            CANCELLED: 'bg-gray-100 text-gray-500',
        };

        const labels: any = {
            DRAFT: 'Brouillon',
            ISSUED: 'Émise',
            PAID: 'Payée',
            LATE: 'En retard',
            CANCELLED: 'Annulée',
        };

        return (
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${styles[status] || styles.DRAFT}`}>
                {labels[status] || status}
            </span>
        );
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-gray-500">Chargement...</div>
            </div>
        );
    }

    return (
        <div>
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Factures</h1>
                    <p className="text-gray-600 mt-2">Gérez vos factures clients et fournisseurs</p>
                </div>
                <Link
                    href="/dashboard/invoices/new"
                    className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition"
                >
                    + Nouvelle facture
                </Link>
            </div>

            {/* Filters */}
            <div className="bg-white p-4 rounded-lg shadow-md mb-6 flex gap-4">
                {['all', 'draft', 'issued', 'paid', 'late'].map((status) => (
                    <button
                        key={status}
                        onClick={() => setFilter(status)}
                        className={`px-4 py-2 rounded-lg font-medium transition ${filter === status
                                ? 'bg-indigo-600 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        {status === 'all' ? 'Toutes' : status.charAt(0).toUpperCase() + status.slice(1)}
                    </button>
                ))}
            </div>

            {/* Invoices Table */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Numéro</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Type</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Date</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Échéance</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Montant</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Statut</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {filteredInvoices.length === 0 ? (
                            <tr>
                                <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                                    Aucune facture trouvée
                                </td>
                            </tr>
                        ) : (
                            filteredInvoices.map((invoice) => (
                                <tr key={invoice.id} className="hover:bg-gray-50 transition">
                                    <td className="px-6 py-4 font-medium">{invoice.number || 'N/A'}</td>
                                    <td className="px-6 py-4">{invoice.type === 'OUT_INVOICE' ? 'Vente' : 'Achat'}</td>
                                    <td className="px- py-4">{new Date(invoice.date_issued).toLocaleDateString('fr-FR')}</td>
                                    <td className="px-6 py-4">{new Date(invoice.date_due).toLocaleDateString('fr-FR')}</td>
                                    <td className="px-6 py-4 font-semibold">{invoice.total_ttc.toFixed(2)} €</td>
                                    <td className="px-6 py-4">{getStatusBadge(invoice.status)}</td>
                                    <td className="px-6 py-4">
                                        <Link
                                            href={`/dashboard/invoices/${invoice.id}`}
                                            className="text-indigo-600 hover:text-indigo-700 font-medium"
                                        >
                                            Voir →
                                        </Link>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
