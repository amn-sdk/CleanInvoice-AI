'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';

interface Customer {
    id: string;
    name: string;
    email: string;
    siret?: string;
    vat_number?: string;
    address?: {
        street?: string;
        city?: string;
        zip?: string;
        country?: string;
    };
}

interface CustomerFormData {
    name: string;
    email: string;
    siret: string;
    vat_number: string;
    street: string;
    city: string;
    zip: string;
    country: string;
}

export default function CustomersPage() {
    const [customers, setCustomers] = useState<Customer[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
    const [formData, setFormData] = useState<CustomerFormData>({
        name: '',
        email: '',
        siret: '',
        vat_number: '',
        street: '',
        city: '',
        zip: '',
        country: 'France',
    });
    const [error, setError] = useState('');

    useEffect(() => {
        fetchCustomers();
    }, []);

    const fetchCustomers = async () => {
        try {
            const response = await apiClient.get('/customers/');
            setCustomers(response.data);
        } catch (err) {
            console.error('Failed to fetch customers', err);
            setError('Impossible de charger les clients');
        } finally {
            setLoading(false);
        }
    };

    const handleOpenModal = (customer?: Customer) => {
        if (customer) {
            setEditingCustomer(customer);
            setFormData({
                name: customer.name,
                email: customer.email,
                siret: customer.siret || '',
                vat_number: customer.vat_number || '',
                street: customer.address?.street || '',
                city: customer.address?.city || '',
                zip: customer.address?.zip || '',
                country: customer.address?.country || 'France',
            });
        } else {
            setEditingCustomer(null);
            setFormData({
                name: '',
                email: '',
                siret: '',
                vat_number: '',
                street: '',
                city: '',
                zip: '',
                country: 'France',
            });
        }
        setShowModal(true);
        setError('');
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingCustomer(null);
        setError('');
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        try {
            const payload = {
                name: formData.name,
                email: formData.email,
                siret: formData.siret || undefined,
                vat_number: formData.vat_number || undefined,
                address: {
                    street: formData.street || undefined,
                    city: formData.city || undefined,
                    zip: formData.zip || undefined,
                    country: formData.country || undefined,
                },
            };

            if (editingCustomer) {
                await apiClient.put(`/customers/${editingCustomer.id}`, payload);
            } else {
                await apiClient.post('/customers/', payload);
            }

            await fetchCustomers();
            handleCloseModal();
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
                setError('Une erreur est survenue');
            }
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Êtes-vous sûr de vouloir supprimer ce client ?')) {
            return;
        }

        try {
            await apiClient.delete(`/customers/${id}`);
            await fetchCustomers();
        } catch (err) {
            console.error('Failed to delete customer', err);
            alert('Impossible de supprimer le client');
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
                    <h1 className="text-3xl font-bold text-gray-900">Clients</h1>
                    <button
                        onClick={() => handleOpenModal()}
                        className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition"
                    >
                        + Ajouter un client
                    </button>
                </div>

                {error && !showModal && (
                    <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg mb-4">
                        {error}
                    </div>
                )}

                <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
                    {customers.length === 0 ? (
                        <div className="p-12 text-center text-gray-500">
                            <p className="text-lg">Aucun client pour le moment</p>
                            <p className="text-sm mt-2">Cliquez sur "Ajouter un client" pour commencer</p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-gray-50 border-b border-gray-200">
                                    <tr>
                                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Nom</th>
                                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Email</th>
                                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">SIRET</th>
                                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">N° TVA</th>
                                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Ville</th>
                                        <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {customers.map((customer) => (
                                        <tr key={customer.id} className="hover:bg-gray-50 transition">
                                            <td className="px-6 py-4 text-sm text-gray-900 font-medium">{customer.name}</td>
                                            <td className="px-6 py-4 text-sm text-gray-600">{customer.email}</td>
                                            <td className="px-6 py-4 text-sm text-gray-600">{customer.siret || '-'}</td>
                                            <td className="px-6 py-4 text-sm text-gray-600">{customer.vat_number || '-'}</td>
                                            <td className="px-6 py-4 text-sm text-gray-600">{customer.address?.city || '-'}</td>
                                            <td className="px-6 py-4 text-sm text-right space-x-2">
                                                <button
                                                    onClick={() => handleOpenModal(customer)}
                                                    className="text-indigo-600 hover:text-indigo-800 font-medium"
                                                >
                                                    Modifier
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(customer.id)}
                                                    className="text-red-600 hover:text-red-800 font-medium"
                                                >
                                                    Supprimer
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            {/* Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <div className="p-6 border-b border-gray-200">
                            <h2 className="text-2xl font-bold text-gray-900">
                                {editingCustomer ? 'Modifier le client' : 'Nouveau client'}
                            </h2>
                        </div>

                        <form onSubmit={handleSubmit} className="p-6 space-y-4">
                            {error && (
                                <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm">
                                    {error}
                                </div>
                            )}

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Nom <span className="text-red-500">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        required
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                                        placeholder="Nom de l'entreprise"
                                    />
                                </div>

                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Email <span className="text-red-500">*</span>
                                    </label>
                                    <input
                                        type="email"
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                        required
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                                        placeholder="contact@entreprise.fr"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">SIRET</label>
                                    <input
                                        type="text"
                                        value={formData.siret}
                                        onChange={(e) => setFormData({ ...formData, siret: e.target.value })}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                                        placeholder="123 456 789 00012"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">N° TVA</label>
                                    <input
                                        type="text"
                                        value={formData.vat_number}
                                        onChange={(e) => setFormData({ ...formData, vat_number: e.target.value })}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                                        placeholder="FR12345678901"
                                    />
                                </div>

                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Adresse</label>
                                    <input
                                        type="text"
                                        value={formData.street}
                                        onChange={(e) => setFormData({ ...formData, street: e.target.value })}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                                        placeholder="123 Rue de la Paix"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Ville</label>
                                    <input
                                        type="text"
                                        value={formData.city}
                                        onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                                        placeholder="Paris"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Code postal</label>
                                    <input
                                        type="text"
                                        value={formData.zip}
                                        onChange={(e) => setFormData({ ...formData, zip: e.target.value })}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                                        placeholder="75001"
                                    />
                                </div>

                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Pays</label>
                                    <input
                                        type="text"
                                        value={formData.country}
                                        onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                                        placeholder="France"
                                    />
                                </div>
                            </div>

                            <div className="flex justify-end space-x-3 pt-4">
                                <button
                                    type="button"
                                    onClick={handleCloseModal}
                                    className="px-6 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition"
                                >
                                    Annuler
                                </button>
                                <button
                                    type="submit"
                                    className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition"
                                >
                                    {editingCustomer ? 'Enregistrer' : 'Créer'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
