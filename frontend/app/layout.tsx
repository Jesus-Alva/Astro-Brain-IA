import type { Metadata } from 'next';
import './globals.css';

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
      </body>
    </html>
  );
}
