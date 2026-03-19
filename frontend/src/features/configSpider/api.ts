import type { ConfigSpiderConfig, RunResult, TestResult } from './types'

const API_BASE_URL =
  (import.meta as any).env?.VITE_API_BASE_URL ?? 'http://localhost:8000/api'

async function request<T>(path: string, options: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers ?? {}),
    },
    ...options,
  })

  if (!response.ok) {
    let detail = response.statusText
    try {
      const data: unknown = await response.json()
      // FastAPI 默认错误结构
      if (typeof data === 'object' && data && 'detail' in data) {
        detail = String((data as { detail: unknown }).detail)
      } else {
        detail = JSON.stringify(data)
      }
    } catch {
      // ignore json parse error
    }
    throw new Error(`请求失败(${response.status}): ${detail}`)
  }

  return response.json() as Promise<T>
}

export function testConfig(config: ConfigSpiderConfig): Promise<TestResult> {
  return request<TestResult>('/config-spider/test', {
    method: 'POST',
    body: JSON.stringify(config),
  })
}

export function runConfig(config: ConfigSpiderConfig): Promise<RunResult> {
  return request<RunResult>('/config-spider/run', {
    method: 'POST',
    body: JSON.stringify(config),
  })
}

export function getExportCsvUrl(): string {
  return `${API_BASE_URL}/config-spider/export/csv`
}
