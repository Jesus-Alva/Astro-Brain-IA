'use client';

import { Toaster } from 'react-hot-toast';

export function Notifications() {
  return (
    <Toaster
      position="top-right"
      gutter={12}
      toastOptions={{
        duration: 3500,
        style: {
          background: '#1f2937',
          color: '#f9fafb',
          border: '1px solid #374151',
          borderRadius: '12px',
          padding: '12px 16px',
          boxShadow: '0 12px 30px rgba(0, 0, 0, 0.2)',
        },
        success: {
          iconTheme: {
            primary: '#22c55e',
            secondary: '#f9fafb',
          },
        },
        error: {
          iconTheme: {
            primary: '#ef4444',
            secondary: '#f9fafb',
          },
        },
      }}
    />
  );
}
