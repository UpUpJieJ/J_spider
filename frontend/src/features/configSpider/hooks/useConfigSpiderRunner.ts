import { useMemo, useState } from 'react'
import { getExportCsvUrl, runConfig, testConfig } from '../api'
import type { ConfigSpiderConfig, RunResult, TestResult } from '../types'

interface UseConfigSpiderRunnerResult {
  testing: boolean
  running: boolean
  error: string | null
  testResult: TestResult | null
  runResult: RunResult | null
  latestItems: Array<Record<string, unknown>>
  latestTotal: number
  executeTest: (config: ConfigSpiderConfig) => Promise<void>
  executeRun: (config: ConfigSpiderConfig) => Promise<void>
  clearError: () => void
  setErrorMessage: (message: string) => void
  exportCsv: () => void
}

export function useConfigSpiderRunner(): UseConfigSpiderRunnerResult {
  const [testing, setTesting] = useState(false)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [testResult, setTestResult] = useState<TestResult | null>(null)
  const [runResult, setRunResult] = useState<RunResult | null>(null)

  const latestItems = useMemo(
    () => runResult?.items ?? testResult?.items ?? [],
    [runResult, testResult],
  )

  const latestTotal = useMemo(
    () => runResult?.total ?? testResult?.total ?? 0,
    [runResult, testResult],
  )

  const executeTest = async (config: ConfigSpiderConfig) => {
    setError(null)
    setRunResult(null)
    setTesting(true)
    try {
      const result = await testConfig(config)
      setTestResult(result)
      if (result.total === 0) {
        setError(
          '⚠️ 未能抓取到任何数据，请检查：\n1. 起始 URL\n2. 列表节点选择器\n3. 字段选择器',
        )
      }
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setTesting(false)
    }
  }

  const executeRun = async (config: ConfigSpiderConfig) => {
    setError(null)
    setRunResult(null)
    setRunning(true)
    try {
      const result = await runConfig(config)
      setRunResult(result)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setRunning(false)
    }
  }

  const exportCsv = () => {
    const url = getExportCsvUrl()
    window.open(url, '_blank', 'noopener')
  }

  return {
    testing,
    running,
    error,
    testResult,
    runResult,
    latestItems,
    latestTotal,
    executeTest,
    executeRun,
    clearError: () => setError(null),
    setErrorMessage: (message: string) => setError(message),
    exportCsv,
  }
}
