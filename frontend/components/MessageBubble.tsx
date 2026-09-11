'use client';

import { Message } from '@/types';

interface MessageBubbleProps {
    message: Message;
    onFeedback?: (esPositivo: boolean) => void;
}

export function MessageBubble({ message, onFeedback }: MessageBubbleProps) {
    const esUsuario = message.role === 'user';

    // Debug: ver el estado del feedback en consola
    if (!esUsuario) {
        console.log('🔍 MessageBubble:', {
            id: message.id,
            feedback: message.feedback,
        });
    }

    return (
        <div
            className={`flex ${esUsuario ? 'justify-end' : 'justify-start'
                } animate-fade-in`}
        >
            <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${esUsuario
                        ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-br-sm'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-bl-sm'
                    }`}
            >
                <div className="whitespace-pre-wrap break-words">{message.content}</div>

                <div
                    className={`text-xs mt-2 ${esUsuario ? 'text-white/60' : 'text-gray-500 dark:text-gray-400'
                        }`}
                >
                    {new Date(message.timestamp).toLocaleTimeString('es-ES', {
                        hour: '2-digit',
                        minute: '2-digit',
                    })}
                </div>

                {!esUsuario && onFeedback && (
                    <div className="flex gap-2 mt-2 pt-2 border-t border-gray-300/50 dark:border-gray-600/50">
                        <button
                            type="button"
                            onClick={() => onFeedback(true)}
                            className={`text-xs px-2 py-1 rounded transition-all duration-200 ${message.feedback === true
                                    ? 'bg-green-600 text-white scale-110'
                                    : 'bg-gray-200 dark:bg-gray-600/50 hover:bg-green-600/50 text-gray-700 dark:text-gray-300'
                                }`}
                            title="Me gustó"
                            aria-label="Me gustó"
                        >
                            👍
                        </button>
                        <button
                            type="button"
                            onClick={() => onFeedback(false)}
                            className={`text-xs px-2 py-1 rounded transition-all duration-200 ${message.feedback === false
                                    ? 'bg-red-600 text-white scale-110'
                                    : 'bg-gray-200 dark:bg-gray-600/50 hover:bg-red-600/50 text-gray-700 dark:text-gray-300'
                                }`}
                            title="No me gustó"
                            aria-label="No me gustó"
                        >
                            👎
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}