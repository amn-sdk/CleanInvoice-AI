'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';

interface CollectionEvent {
    id: string;
    type: string;
    channel: string;
    content: string;
    metadata: Record<string, unknown>;
    created_at: string;
}

interface CollectionCase {
    case_id: string;
    invoice_id: string;
    invoice_number: string;
    customer_name: string;
    amount_due: number;
    days_overdue: number;
    status: string;
    strategy: string;
    level: number;
    timeline: CollectionEvent[];
}

const statusColors: Record<string, string> = {
    'OPEN': 'bg-yellow-100 text-yellow-800',
    'IN_PROGRESS': 'bg-blue-100 text-blue-800',
    'CLOSED_PAID': 'bg-green-100 text-green-800',
    'CLOSED_LOST': 'bg-red-100 text-red-800',
};

const statusLabels: Record<string, string> = {
    'OPEN': 'Ouvert',
    'IN_PROGRESS': 'En cours',
    'CLOSED_PAID': 'Payé',
    'CLOSED_LOST': 'Perdu',
};

export default function CollectionsPage() {
    const [cases, setCases] = useState<CollectionCase[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedCase, setSelectedCase] = useState<CollectionCase | null>(null);
    const [error, setError] = useState('');
    const [actionLoading, setActionLoading] = useState(false);

    useEffect(() => {
        fetchCases();
    }, []);

    const fetchCases = async () => {
        try {
            // For now, we'll fetch invoices and check which have collection cases
            const invoicesResponse = await apiClient.get('/invoices/');
            const invoices = invoicesResponse.data;

            // Fetch collection timeline for each invoice
            const casesData: CollectionCase[] = [];
            for (const invoice of invoices) {
                try {
                    const timelineResponse = await apiClient.get(`/collections/invoices/${invoice.id}/timeline`);
                    const timeline = timelineResponse.data;

                    if (timeline.has_case) {
                        const daysOverdue = invoice.date_due
                            ? Math.floor((new Date().getTime() - new Date(invoice.date_due).getTime()) / (1000 * 60 * 60 * 24))
                            : 0;

                        casesData.push({
                            case_id: timeline.case_id,
                            invoice_id: invoice.id,
                            invoice_number: invoice.number || 'DRAFT',
                            customer_name: invoice.customer?.name || 'Unknown',
                            amount_due: parseFloat(invoice.total_ttc),
                            days_overdue: daysOverdue,
                            status: timeline.status,
                            strategy: timeline.strategy,
                            level: timeline.level,
                            timeline: timeline.timeline,
                        });
                    }
                } catch (err) {
                    console.error(`Failed to fetch timeline for invoice ${invoice.id}`, err);
                }
            }

            setCases(casesData);
        } catch (err) {
            console.error('Failed to fetch collection cases', err);
            setError('Impossible de charger les dossiers de recouvrement');
        } finally {
            setLoading(false);
        }
    };

    const handleStartCollection = async (invoiceId: string) => {
        setActionLoading(true);
        setError('');

        try {
            await apiClient.post(`/collections/invoices/${invoiceId}/start`, {
                strategy: 'STANDARD'
            });
            await fetchCases();
            alert('Recouvrement démarré avec succès !');
        } catch (err: unknown) {
            interface AxiosError {
                response?: {
                    data?: {
                        detail?: string;
                    };
                };
            }
            const isAxiosError = (error: unknown): error is AxiosError => {
                return typeof error === 'object' && error !== null && 'response' in error;
            };

            if (isAxiosError(err) && err.response?.data?.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Impossible de démarrer le recouvrement');
            }
        } finally {
            setActionLoading(false);
        }
    };

    const handleCloseCase = async (caseId: string, reason: string) => {
        if (!confirm(`Êtes-vous sûr de vouloir clôturer ce dossier comme "${reason}" ?`)) {
            return;
        }

        setActionLoading(true);
        setError('');

        try {
            await apiClient.put(`/collections/cases/${caseId}/close`, null, {
                params: { reason }
            });
            await fetchCases();
            setSelectedCase(null);
            alert('Dossier clôturé avec succès !');
        } catch (err) {
            console.error('Failed to close case', err);
            setError('Impossible de clôturer le dossier');
        } finally {
            setActionLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-gray-600">Chargement...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Recouvrement</h1>
                        <p className="text-gray-600 mt-1">Gestion des factures impayées</p>
                    </div>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg mb-4">
                        {error}
                    </div>
                )}

                {cases.length === 0 ? (
                    <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
                        <p className="text-lg text-gray-500">Aucun dossier de recouvrement en cours</p>
                        <p className="text-sm text-gray-400 mt-2">Les factures impayées apparaîtront ici</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {cases.map((collectionCase) => (
                            <div
                                key={collectionCase.case_id}
                                className="bg-white rounded-2xl shadow-xl overflow-hidden hover:shadow-2xl transition cursor-pointer"
                                onClick={() => setSelectedCase(collectionCase)}
                            >
                                <div className="p-6">
                                    <div className="flex justify-between items-start mb-4">
                                        <div>
                                            <h3 className="text-xl font-bold text-gray-900">
                                                {collectionCase.invoice_number}
                                            </h3>
                                            <p className="text-gray-600">{collectionCase.customer_name}</p>
                                        </div>
                                        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${statusColors[collectionCase.status] || 'bg-gray-100 text-gray-800'}`}>
                                            {statusLabels[collectionCase.status] || collectionCase.status}
                                        </span>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4 mb-4">
                                        <div>
                                            <p className="text-sm text-gray-500">Montant dû</p>
                                            <p className="text-2xl font-bold text-indigo-600">
                                                {collectionCase.amount_due.toFixed(2)} €
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-500">Jours de retard</p>
                                            <p className="text-2xl font-bold text-red-600">
                                                {collectionCase.days_overdue}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between text-sm text-gray-500">
                                        <span>Niveau {collectionCase.level}</span>
                                        <span>{collectionCase.timeline.length} événement(s)</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Detail Modal */}
            {selectedCase && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
                        <div className="p-6 border-b border-gray-200">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h2 className="text-2xl font-bold text-gray-900">
                                        Facture {selectedCase.invoice_number}
                                    </h2>
                                    <p className="text-gray-600">{selectedCase.customer_name}</p>
                                </div>
                                <button
                                    onClick={() => setSelectedCase(null)}
                                    className="text-gray-400 hover:text-gray-600"
                                >
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                        <div className="p-6">
                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div className="bg-indigo-50 p-4 rounded-lg">
                                    <p className="text-sm text-indigo-600 font-medium">Montant dû</p>
                                    <p className="text-3xl font-bold text-indigo-900">
                                        {selectedCase.amount_due.toFixed(2)} €
                                    </p>
                                </div>
                                <div className="bg-red-50 p-4 rounded-lg">
                                    <p className="text-sm text-red-600 font-medium">Jours de retard</p>
                                    <p className="text-3xl font-bold text-red-900">
                                        {selectedCase.days_overdue}
                                    </p>
                                </div>
                            </div>

                            <h3 className="text-lg font-bold text-gray-900 mb-4">Historique des événements</h3>

                            {selectedCase.timeline.length === 0 ? (
                                <p className="text-gray-500 text-center py-8">Aucun événement</p>
                            ) : (
                                <div className="space-y-4">
                                    {selectedCase.timeline.map((event, index) => (
                                        <div key={event.id} className="flex gap-4">
                                            <div className="flex flex-col items-center">
                                                <div className={`w-3 h-3 rounded-full ${index === 0 ? 'bg-indigo-600' : 'bg-gray-300'}`} />
                                                {index < selectedCase.timeline.length - 1 && (
                                                    <div className="w-0.5 h-full bg-gray-200 mt-1" />
                                                )}
                                            </div>
                                            <div className="flex-1 pb-4">
                                                <div className="flex justify-between items-start mb-1">
                                                    <span className="font-medium text-gray-900">
                                                        {event.type.replace('_', ' ')}
                                                    </span>
                                                    <span className="text-sm text-gray-500">
                                                        {new Date(event.created_at).toLocaleDateString('fr-FR')}
                                                    </span>
                                                </div>
                                                <p className="text-sm text-gray-600">{event.content}</p>
                                                {event.channel && (
                                                    <span className="inline-block mt-2 px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                                                        {event.channel}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            <div className="flex justify-end space-x-3 mt-6 pt-6 border-t border-gray-200">
                                {selectedCase.status === 'OPEN' && (
                                    <>
                                        <button
                                            onClick={() => handleCloseCase(selectedCase.case_id, 'paid')}
                                            disabled={actionLoading}
                                            className="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition disabled:opacity-50"
                                        >
                                            Marquer comme payé
                                        </button>
                                        <button
                                            onClick={() => handleCloseCase(selectedCase.case_id, 'lost')}
                                            disabled={actionLoading}
                                            className="px-6 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition disabled:opacity-50"
                                        >
                                            Abandonner
                                        </button>
                                    </>
                                )}
                                <button
                                    onClick={() => setSelectedCase(null)}
                                    className="px-6 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition"
                                >
                                    Fermer
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
