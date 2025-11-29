'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';

interface InvoiceLine {
    id: string;
    description: string;
    quantity: number;
    unit_price: number;
    vat_rate: number;
    amount_ht: number;
}

interface Invoice {
    id: string;
    type: string;
    status: string;
    number: string;
    date_issued: string;
    date_due: string;
    total_ht: number;
    total_tva: number;
    total_ttc: number;
    lines: InvoiceLine[];
}

export default function InvoiceDetailPage({ params }: { params: { id: string } }) {
    const router = useRouter();
    const [invoice, setInvoice] = useState<Invoice | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchInvoice = async () => {
            try {
                const response = await apiClient.get(`/invoices/${params.id}`);
                setInvoice(response.data);
            } catch (error) {
                console.error('Failed to fetch invoice', error);
                router.push('/dashboard/invoices');
            } finally {
                setLoading(false);
            }
        };

        fetchInvoice();
    }, [params.id, router]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-gray-500">Chargement...</div>
            </div>
        );
    }

    if (!invoice) {
        return null;
    }

    return (
        <div>
            <button
                onClick={() => router.back()}
                className="mb-6 text-indigo-600 hover:text-indigo-700 font-medium"
            >
                ← Retour
            </button>

            <div className="bg-white rounded-xl shadow-md p-8">
                <div className="flex items-start justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">
                            Facture {invoice.number || 'Brouillon'}
                        </h1>
                        <p className="text-gray-600 mt-2">
                            Type : {invoice.type === 'OUT_INVOICE' ? 'Facture client' : 'Facture fournisseur'}
                        </p>
                    </div>
                    <span className={`px-4 py-2 rounded-lg font-semibold ${invoice.status === 'PAID' ? 'bg-green-100 text-green-700' :
                            invoice.status === 'ISSUED' ? 'bg-blue-100 text-blue-700' :
                                invoice.status === 'LATE' ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-700'
                        }`}>
                        {invoice.status}
                    </span>
                </div>

                <div className="grid grid-cols-2 gap-8 mb-8">
                    <div>
                        <h3 className="font-semibold text-gray-700 mb-2">Date d&apos;émission</h3>
                        <p className="text-lg">{new Date(invoice.date_issued).toLocaleDateString('fr-FR')}</p>
                    </div>
                    <div>
                        <h3 className="font-semibold text-gray-700 mb-2">Date d&apos;échéance</h3>
                        <p className="text-lg">{new Date(invoice.date_due).toLocaleDateString('fr-FR')}</p>
                    </div>
                </div>

                <div className="border-t border-gray-200 pt-6">
                    <h3 className="font-semibold text-gray-900 mb-4">Lignes de facturation</h3>
                    <table className="w-full">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-3 text-left text-sm font-semibold">Description</th>
                                <th className="px-4 py-3 text-right text-sm font-semibold">Quantité</th>
                                <th className="px-4 py-3 text-right text-sm font-semibold">Prix unitaire</th>
                                <th className="px-4 py-3 text-right text-sm font-semibold">TVA</th>
                                <th className="px-4 py-3 text-right text-sm font-semibold">Total HT</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {invoice.lines.map((line) => (
                                <tr key={line.id}>
                                    <td className="px-4 py-3">{line.description}</td>
                                    <td className="px-4 py-3 text-right">{line.quantity}</td>
                                    <td className="px-4 py-3 text-right">{line.unit_price.toFixed(2)} €</td>
                                    <td className="px-4 py-3 text-right">{line.vat_rate}%</td>
                                    <td className="px-4 py-3 text-right font-semibold">{line.amount_ht.toFixed(2)} €</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div className="border-t border-gray-200 mt-6 pt-6">
                    <div className="flex justify-end">
                        <div className="w-64 space-y-2">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Total HT</span>
                                <span className="font-semibold">{invoice.total_ht.toFixed(2)} €</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">TVA</span>
                                <span className="font-semibold">{invoice.total_tva.toFixed(2)} €</span>
                            </div>
                            <div className="flex justify-between text-lg border-t border-gray-200 pt-2">
                                <span className="font-bold">Total TTC</span>
                                <span className="font-bold text-indigo-600">{invoice.total_ttc.toFixed(2)} €</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
