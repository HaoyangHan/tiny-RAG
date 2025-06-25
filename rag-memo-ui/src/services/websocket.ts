/**
 * WebSocket service for real-time updates in TinyRAG v1.4.1
 * Provides real-time notifications for generation completion, document processing, etc.
 */

import { useEffect, useRef, useCallback } from 'react';

export interface WebSocketMessage {
  type: 'generation_completed' | 'generation_failed' | 'document_processed' | 'element_executed' | 'evaluation_created' | 'project_updated';
  data: any;
  timestamp: string;
  project_id?: string;
  user_id?: string;
}

export interface WebSocketConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export class WebSocketService {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private isConnecting = false;
  
  constructor(config: WebSocketConfig) {
    this.config = {
      reconnectInterval: 5000,
      maxReconnectAttempts: 5,
      ...config
    };
  }

  connect(): void {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.isConnecting = true;

    try {
      this.ws = new WebSocket(this.config.url);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.config.onConnect?.();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.config.onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnecting = false;
        this.ws = null;
        this.config.onDisconnect?.();
        this.scheduleReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
        this.config.onError?.(error);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  disconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= (this.config.maxReconnectAttempts || 5)) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectTimeout = setTimeout(() => {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})`);
      this.connect();
    }, this.config.reconnectInterval);
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

/**
 * React hook for WebSocket connection
 */
export const useWebSocket = (projectId?: string) => {
  const wsRef = useRef<WebSocketService | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.isConnected()) {
      return;
    }

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    const url = projectId ? `${wsUrl}/ws/projects/${projectId}` : `${wsUrl}/ws`;

    wsRef.current = new WebSocketService({
      url,
      onMessage: (message: WebSocketMessage) => {
        // Dispatch custom events for components to listen to
        window.dispatchEvent(new CustomEvent('websocket-message', { detail: message }));
      },
      onConnect: () => {
        console.log('WebSocket connected for project:', projectId);
        window.dispatchEvent(new CustomEvent('websocket-connected'));
      },
      onDisconnect: () => {
        console.log('WebSocket disconnected');
        window.dispatchEvent(new CustomEvent('websocket-disconnected'));
      },
      onError: (error) => {
        console.error('WebSocket error:', error);
        window.dispatchEvent(new CustomEvent('websocket-error', { detail: error }));
      }
    });

    wsRef.current.connect();
  }, [projectId]);

  const disconnect = useCallback(() => {
    wsRef.current?.disconnect();
    wsRef.current = null;
  }, []);

  const sendMessage = useCallback((message: any) => {
    wsRef.current?.send(message);
  }, []);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    connect,
    disconnect,
    sendMessage,
    isConnected: () => wsRef.current?.isConnected() || false
  };
};

/**
 * Hook for listening to specific WebSocket message types
 */
export const useWebSocketMessage = (
  messageType: WebSocketMessage['type'],
  handler: (data: any) => void,
  dependencies: any[] = []
) => {
  useEffect(() => {
    const handleMessage = (event: CustomEvent<WebSocketMessage>) => {
      if (event.detail.type === messageType) {
        handler(event.detail.data);
      }
    };

    window.addEventListener('websocket-message', handleMessage as EventListener);

    return () => {
      window.removeEventListener('websocket-message', handleMessage as EventListener);
    };
  }, [messageType, handler, ...dependencies]);
}; 