import type { Metadata } from 'next';
import { Suspense } from 'react';
import './globals.css';
import { Providers } from './providers';
import { AppLayout } from '@/components/layout/AppLayout';

export const metadata: Metadata = {
  title: 'Next.Epoch - AI Frontier Intelligence',
  description: 'Track the cutting edge of AI research and development',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans bg-gray-50">
        <Providers>
          <Suspense fallback={
            <div className="min-h-screen flex items-center justify-center">
              <div className="animate-pulse text-gray-500">Loading...</div>
            </div>
          }>
            <AppLayout>{children}</AppLayout>
          </Suspense>
        </Providers>
      </body>
    </html>
  );
}
