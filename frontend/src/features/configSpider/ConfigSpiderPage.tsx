import React, { useState } from 'react'
import { ConfigPanel } from './components/ConfigPanel'
import { ResultPanel } from './components/ResultPanel'
import { defaultConfig, emptyField } from './constants'
import { useConfigSpiderRunner } from './hooks/useConfigSpiderRunner'
import { normalizeConfigForSubmit } from './normalize'
import type {
  ConfigSpiderConfig,
  FieldConfig,
  FieldFromPage,
  FieldScope,
  SelectorType,
} from './types'
import { validateBeforeRun, validateBeforeTest } from './validation'

export const ConfigSpiderPage: React.FC = () => {
  const [config, setConfig] = useState<ConfigSpiderConfig>(defaultConfig)
  const runner = useConfigSpiderRunner()
  const urlCount = config.start_urls.filter((url) => url.trim().length > 0).length
  const fullFieldCount = config.fields.filter(
    (field) => field.name.trim().length > 0 && field.selector.trim().length > 0,
  ).length
  const pageMode = config.list_selector.trim().length > 0 ? '列表模式' : '单页模式'
  const dedupText = config.enable_dedup ? '开启' : '关闭'
  const statusText = runner.running
    ? '爬取中'
    : runner.testing
      ? '测试中'
      : runner.latestItems.length > 0
        ? '已完成'
        : '待运行'

  const handleBasicChange = (
    key: keyof Pick<
      ConfigSpiderConfig,
      'target_name' | 'list_selector' | 'detail_url_selector' | 'next_page_selector'
    >,
    value: string,
  ) => {
    setConfig((prev) => ({ ...prev, [key]: value }))
  }

  const handleSelectorTypeChange = (value: SelectorType) => {
    setConfig((prev) => ({ ...prev, selector_type: value }))
  }

  const handleStartUrlChange = (index: number, value: string) => {
    setConfig((prev) => {
      const startUrls = [...prev.start_urls]
      startUrls[index] = value
      return { ...prev, start_urls: startUrls }
    })
  }

  const addStartUrl = () => {
    setConfig((prev) => ({ ...prev, start_urls: [...prev.start_urls, ''] }))
  }

  const removeStartUrl = (index: number) => {
    setConfig((prev) => ({
      ...prev,
      start_urls: prev.start_urls.filter((_, i) => i !== index),
    }))
  }

  const updateField = (
    index: number,
    key: keyof FieldConfig,
    value: string | FieldFromPage | FieldScope,
  ) => {
    setConfig((prev) => {
      const fields = [...prev.fields]
      fields[index] = { ...fields[index], [key]: value }
      return { ...prev, fields }
    })
  }

  const addField = () => {
    setConfig((prev) => ({ ...prev, fields: [...prev.fields, emptyField()] }))
  }

  const removeField = (index: number) => {
    setConfig((prev) => ({
      ...prev,
      fields: prev.fields.filter((_, i) => i !== index),
    }))
  }

  const handleRunParamChange = (key: 'concurrency' | 'download_delay' | 'max_items', value: string) => {
    setConfig((prev) => {
      if (value === '') {
        if (key === 'max_items') return { ...prev, max_items: null }
        if (key === 'concurrency') return { ...prev, concurrency: defaultConfig.concurrency }
        return { ...prev, download_delay: defaultConfig.download_delay }
      }
      const num = Number(value)
      if (Number.isNaN(num)) {
        return prev
      }
      if (key === 'max_items') {
        return { ...prev, max_items: Math.max(1, Math.floor(num)) }
      }
      if (key === 'concurrency') {
        return { ...prev, concurrency: Math.max(1, Math.floor(num)) }
      }
      return { ...prev, download_delay: Math.max(0, num) }
    })
  }

  const handleDedupChange = (enabled: boolean) => {
    setConfig((prev) => ({ ...prev, enable_dedup: enabled }))
  }

  const handleTest = async () => {
    const error = validateBeforeTest(config)
    if (error) {
      runner.setErrorMessage(error)
      return
    }
    const payload = normalizeConfigForSubmit(config)
    await runner.executeTest(payload)
  }

  const handleRun = async () => {
    const error = validateBeforeRun(config)
    if (error) {
      runner.setErrorMessage(error)
      return
    }
    const payload = normalizeConfigForSubmit(config)
    await runner.executeRun(payload)
  }

  return (
    <div className="app-root">
      <header className="app-header">
        <div className="app-title">
          <span className="brand-chip">Config Spider Studio</span>
          <h1>可视化配置爬虫工作台</h1>
          <p>通过表单快速配置列表/详情页选择器，实时测试并导出结构化结果。</p>
        </div>
        <div className="header-tips">
          <span className="tip-badge">推荐流程</span>
          <span className="tip-text">填写 URL → 配置字段 → 测试一页 → 正式运行 → 导出 CSV</span>
        </div>
        <div className="header-metrics">
          <div className="metric-card">
            <span className="metric-label">起始 URL</span>
            <strong className="metric-value">{urlCount}</strong>
          </div>
          <div className="metric-card">
            <span className="metric-label">完整字段</span>
            <strong className="metric-value">{fullFieldCount}</strong>
          </div>
          <div className="metric-card">
            <span className="metric-label">抓取模式</span>
            <strong className="metric-value metric-text">{pageMode}</strong>
          </div>
          <div className="metric-card">
            <span className="metric-label">请求去重</span>
            <strong className="metric-value metric-text">{dedupText}</strong>
          </div>
          <div className="metric-card">
            <span className="metric-label">运行状态</span>
            <strong className="metric-value metric-text">{statusText}</strong>
          </div>
        </div>
      </header>

      <main className="layout">
        <ConfigPanel
          config={config}
          onBasicChange={handleBasicChange}
          onSelectorTypeChange={handleSelectorTypeChange}
          onStartUrlChange={handleStartUrlChange}
          onAddStartUrl={addStartUrl}
          onRemoveStartUrl={removeStartUrl}
          onUpdateField={updateField}
          onAddField={addField}
          onRemoveField={removeField}
          onRunParamChange={handleRunParamChange}
          onDedupChange={handleDedupChange}
        />
        <ResultPanel
          testing={runner.testing}
          running={runner.running}
          error={runner.error}
          latestItems={runner.latestItems}
          latestTotal={runner.latestTotal}
          maxItems={config.max_items}
          onTest={handleTest}
          onRun={handleRun}
          onExport={runner.exportCsv}
        />
      </main>
    </div>
  )
}
