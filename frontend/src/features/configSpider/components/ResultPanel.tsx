import React from 'react'

interface ResultPanelProps {
  testing: boolean
  running: boolean
  error: string | null
  latestItems: Array<Record<string, unknown>>
  latestTotal: number
  maxItems?: number | null
  onTest: () => void
  onRun: () => void
  onExport: () => void
}

function renderTable(
  latestItems: Array<Record<string, unknown>>,
  latestTotal: number,
  maxItems?: number | null,
) {
  if (!latestItems.length) {
    return (
      <div className="empty-result">
        <div className="empty-icon">📋</div>
        <p className="empty-title">还没有抓取结果</p>
        <p className="empty-desc">
          请先在左侧配置好选择器，然后点击「测试一条/一页」或「开始爬取」。
        </p>
      </div>
    )
  }

  const columns = Object.keys(latestItems[0] ?? {})
  return (
    <div className="result-table-wrapper">
      <table className="result-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {latestItems.map((row, idx) => (
            <tr key={idx}>
              {columns.map((col) => (
                <td key={col}>
                  {String((row as Record<string, unknown>)[col] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="result-meta">
        <span>成功抓取 {latestTotal} 条数据</span>
        {maxItems ? <span className="meta-tag">已限制最多 {maxItems} 条</span> : null}
      </div>
    </div>
  )
}

export const ResultPanel: React.FC<ResultPanelProps> = ({
  testing,
  running,
  error,
  latestItems,
  latestTotal,
  maxItems,
  onTest,
  onRun,
  onExport,
}) => {
  const stateLabel = running ? '正在执行正式抓取' : testing ? '正在执行测试' : '等待运行'

  return (
    <section className="panel panel-right">
      <h2>运行与结果</h2>
      <div className="status-strip">
        <span className="status-dot" />
        <span>{stateLabel}</span>
      </div>
      <div className="run-actions">
        <button type="button" className="secondary" onClick={onTest} disabled={testing || running}>
          {testing ? '测试中…' : '测试一条/一页'}
        </button>
        <button type="button" onClick={onRun} disabled={running}>
          {running ? '正在爬取…' : '开始爬取'}
        </button>
        <button type="button" className="secondary" onClick={onExport} disabled={!latestItems.length}>
          导出 CSV
        </button>
      </div>

      {error ? <div className="error-banner">{error}</div> : null}

      <div className="preview">
        {renderTable(latestItems, latestTotal, maxItems)}
      </div>
    </section>
  )
}
