import { QueryRequest, QueryResponse, HealthResponse } from '../types';

const API_URL = 'http://10.0.2.2:8080'; // Android emulator -> host
// For iOS simulator use: http://localhost:8080
// For physical device, use your machine's local IP

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  const resp = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!resp.ok) {
    const error = await resp.text();
    throw new Error(`API error ${resp.status}: ${error}`);
  }
  return resp.json();
}

export async function healthCheck(): Promise<HealthResponse> {
  return request<HealthResponse>('/health');
}

export async function sendQuery(text: string, language = 'en'): Promise<QueryResponse> {
  return request<QueryResponse>('/query', {
    method: 'POST',
    body: JSON.stringify({ text, language } as QueryRequest),
  });
}

export async function uploadImage(uri: string): Promise<QueryResponse> {
  const formData = new FormData();
  formData.append('file', {
    uri,
    type: 'image/jpeg',
    name: 'document.jpg',
  } as any);

  const resp = await fetch(`${API_URL}/query/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!resp.ok) {
    const error = await resp.text();
    throw new Error(`Upload error ${resp.status}: ${error}`);
  }
  return resp.json();
}
