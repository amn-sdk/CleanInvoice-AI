'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/auth';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const router = useRouter();
    const { isAuthenticated, user, logout } = useAuthStore();

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
        }
    }, [isAuthenticated, router]);

    if (!isAuthenticated) {
        return null;
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Sidebar */}
            <aside className="fixed top-0 left-0 h-screen w-64 bg-white border-r border-gray-200 flex flex-col">
                <div className="p-6 border-b border-gray-200">
                    <h1 className="text-2xl font-bold text-indigo-600">CleanInvoice</h1>
                    {user && (
                        <p className="text-sm text-gray-600 mt-2">{user.full_name}</p>
                    )}
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    <Link
                        href="/dashboard"
                        className="block px-4 py-3 rounded-lg hover:bg-indigo-50 hover:text-indigo-600 transition font-medium"
                    >
                        📊 Dashboard
                    </Link>
                    <Link
                        href="/dashboard/invoices"
                        className="block px-4 py-3 rounded-lg hover:bg-indigo-50 hover:text-indigo-600 transition font-medium"
                    >
                        📄 Factures
                    </Link>
                    <Link
                        href="/dashboard/customers"
                        className="block px-4 py-3 rounded-lg hover:bg-indigo-50 hover:text-indigo-600 transition font-medium"
                    >
                        👥 Clients
                    </Link>
                    <Link
                        href="/dashboard/collections"
                        className="block px-4 py-3 rounded-lg hover:bg-indigo-50 hover:text-indigo-600 transition font-medium"
                    >
                        💰 Recouvrement
                    </Link>
                </nav>

                <div className="p-4 border-t border-gray-200">
                    <button
                        onClick={logout}
                        className="w-full px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition font-medium"
                    >
                        Déconnexion
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="ml-64 p-8">
                {children}
            </main>
        </div>
    );
}
