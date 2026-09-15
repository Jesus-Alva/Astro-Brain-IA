import type { Metadata } from 'next';
import './globals.css';
import { Notifications } from '@/components/Notifications';

export const metadata: Metadata = {
  title: 'Astro-IA - Tu IA Personal',
  description: 'IA Personal con aprendizaje continuo y memoria semántica',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="dark" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Exo:ital,wght@0,100..900;1,100..900&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Roboto:ital,wght@0,100..900;1,100..900&display=swap"
          rel="stylesheet"
        />
        {/* Script para aplicar el tema antes de la hidratación */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  const tema = localStorage.getItem('tema') || 'oscuro';
                  if (tema === 'oscuro') {
                    document.documentElement.classList.add('dark');
                  } else {
                    document.documentElement.classList.remove('dark');
                  }
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body className="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white transition-colors duration-300">
        {children}
        <Notifications />
      </body>
    </html>
  );
}
