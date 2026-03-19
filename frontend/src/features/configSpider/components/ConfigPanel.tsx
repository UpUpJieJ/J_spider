import React from 'react'
import type {
  ConfigSpiderConfig,
  FieldConfig,
  FieldFromPage,
  FieldScope,
  SelectorType,
} from '../types'

const BUILTIN_ATTRS = ['text', 'href', 'src', 'title'] as const
type BuiltinAttr = (typeof BUILTIN_ATTRS)[number]

function isBuiltinAttr(value: string): value is BuiltinAttr {
  return BUILTIN_ATTRS.includes(value as BuiltinAttr)
}

interface ConfigPanelProps {
  config: ConfigSpiderConfig
  onBasicChange: (
    key: keyof Pick<
      ConfigSpiderConfig,
      'target_name' | 'list_selector' | 'detail_url_selector' | 'next_page_selector'
    >,
    value: string,
  ) => void
  onSelectorTypeChange: (value: SelectorType) => void
  onStartUrlChange: (index: number, value: string) => void
  onAddStartUrl: () => void
  onRemoveStartUrl: (index: number) => void
  onUpdateField: (
    index: number,
    key: keyof FieldConfig,
    value: string | FieldFromPage | FieldScope,
  ) => void
  onAddField: () => void
  onRemoveField: (index: number) => void
  onRunParamChange: (key: 'concurrency' | 'download_delay' | 'max_items', value: string) => void
  onDedupChange: (enabled: boolean) => void
}

export const ConfigPanel: React.FC<ConfigPanelProps> = ({
  config,
  onBasicChange,
  onSelectorTypeChange,
  onStartUrlChange,
  onAddStartUrl,
  onRemoveStartUrl,
  onUpdateField,
  onAddField,
  onRemoveField,
  onRunParamChange,
  onDedupChange,
}) => (
  <section className="panel panel-left">
    <h2>配置</h2>

    <div className="section">
      <div className="section-head">
        <span className="step-index">1</span>
        <h3>基本信息</h3>
      </div>
      <p className="section-desc">先定义目标站点和解析器类型，后续所有选择器都会基于这个上下文。</p>
      <div className="field-row">
        <label>爬虫名称</label>
        <input
          value={config.target_name}
          onChange={(e) => onBasicChange('target_name', e.target.value)}
          placeholder="news_spider"
        />
      </div>

      <div className="field-row">
        <label>起始 URL</label>
        <div className="stack">
          {config.start_urls.map((url, index) => (
            <div key={index} className="inline-row">
              <input
                value={url}
                onChange={(e) => onStartUrlChange(index, e.target.value)}
                placeholder="https://example.com/list?page=1"
              />
              <button
                type="button"
                className="secondary"
                onClick={() => onRemoveStartUrl(index)}
                disabled={config.start_urls.length === 1}
              >
                删除
              </button>
            </div>
          ))}
          <button type="button" className="secondary" onClick={onAddStartUrl}>
            添加一行
          </button>
        </div>
      </div>

      <div className="field-row">
        <label>选择器类型 <span className="required">*</span></label>
        <select
          value={config.selector_type}
          onChange={(e) => onSelectorTypeChange(e.target.value as SelectorType)}
        >
          <option value="css">CSS 选择器</option>
          <option value="xpath">XPath 选择器</option>
        </select>
        <p className="field-help">
          CSS 更直观，XPath 更灵活。建议先统一一种风格，避免维护成本升高。
        </p>
      </div>
    </div>

    <div className="section">
      <div className="section-head">
        <span className="step-index">2</span>
        <h3>列表与详情配置</h3>
      </div>
      <p className="section-desc">配置列表节点、详情入口和分页规则，决定爬虫的抓取路径。</p>
      <div className="field-row">
        <label>列表节点选择器</label>
        <input
          value={config.list_selector}
          onChange={(e) => onBasicChange('list_selector', e.target.value)}
          placeholder={config.selector_type === 'css' ? '.item' : '//div[@class="item"]'}
        />
      </div>
      <div className="field-row">
        <label>详情页 URL 选择器</label>
        <input
          value={config.detail_url_selector ?? ''}
          onChange={(e) => onBasicChange('detail_url_selector', e.target.value)}
          placeholder={config.selector_type === 'css' ? 'a.detail-link' : './/a[@class="detail"]'}
        />
      </div>
      <div className="field-row">
        <label>下一页 URL 选择器</label>
        <input
          value={config.next_page_selector ?? ''}
          onChange={(e) => onBasicChange('next_page_selector', e.target.value)}
          placeholder={config.selector_type === 'css' ? 'a.next-page' : '//a[@rel="next"]'}
        />
      </div>
    </div>

    <div className="section">
      <div className="section-head">
        <span className="step-index">3</span>
        <h3>字段配置 <span className="section-tip">定义要提取的数据字段</span></h3>
      </div>
      <p className="section-desc">每行对应一个输出字段。字段名和选择器必须同时填写。</p>
      <div className="fields-table">
        <div className="fields-header">
          <span>字段名</span>
          <span>页面</span>
          <span>作用域</span>
          <span>选择器</span>
          <span>属性</span>
          <span />
        </div>
        {config.fields.map((field, index) => {
          const attrMode = isBuiltinAttr(field.attr) ? field.attr : 'custom'
          const customAttr = isBuiltinAttr(field.attr) ? '' : field.attr
          return (
            <React.Fragment key={index}>
              <div className="fields-row">
                <input
                  value={field.name}
                  onChange={(e) => onUpdateField(index, 'name', e.target.value)}
                  placeholder="title"
                />
                <select
                  value={field.from_page}
                  onChange={(e) => onUpdateField(index, 'from_page', e.target.value as FieldFromPage)}
                >
                  <option value="list">列表页</option>
                  <option value="detail">详情页</option>
                </select>
                <select
                  value={field.scope}
                  onChange={(e) => onUpdateField(index, 'scope', e.target.value as FieldScope)}
                >
                  <option value="node">节点</option>
                  <option value="page">整页</option>
                </select>
                <input
                  value={field.selector}
                  onChange={(e) => onUpdateField(index, 'selector', e.target.value)}
                  placeholder={config.selector_type === 'css' ? '.title' : './/h2'}
                />
                <select
                  value={attrMode}
                  onChange={(e) => {
                    const next = e.target.value
                    if (next === 'custom') {
                      onUpdateField(index, 'attr', customAttr)
                      return
                    }
                    onUpdateField(index, 'attr', next)
                  }}
                >
                  <option value="text">文本</option>
                  <option value="href">href</option>
                  <option value="src">src</option>
                  <option value="title">title</option>
                  <option value="custom">自定义属性</option>
                </select>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => onRemoveField(index)}
                  disabled={config.fields.length === 1}
                >
                  删除
                </button>
              </div>
              {attrMode === 'custom' ? (
                <div className="fields-row-custom">
                  <span>自定义属性名</span>
                  <input
                    value={customAttr}
                    onChange={(e) => onUpdateField(index, 'attr', e.target.value)}
                    placeholder="title / data-id / aria-label"
                  />
                </div>
              ) : null}
            </React.Fragment>
          )
        })}
      </div>
      <button type="button" className="secondary" onClick={onAddField}>
        添加字段
      </button>
    </div>

    <div className="section">
      <div className="section-head">
        <span className="step-index">4</span>
        <h3>运行参数 <span className="section-tip">控制爬虫速度和抓取范围</span></h3>
      </div>
      <div className="field-row inline">
        <label>并发数</label>
        <input
          type="number"
          min={1}
          value={config.concurrency}
          onChange={(e) => onRunParamChange('concurrency', e.target.value)}
        />
        <label>下载延时（秒）</label>
        <input
          type="number"
          min={0}
          step={0.1}
          value={config.download_delay}
          onChange={(e) => onRunParamChange('download_delay', e.target.value)}
        />
        <label>最多抓取条数</label>
        <input
          type="number"
          min={1}
          value={config.max_items ?? ''}
          onChange={(e) => onRunParamChange('max_items', e.target.value)}
          placeholder="不填表示不限制"
        />
      </div>
      <div className="field-row">
        <label>请求去重</label>
        <select
          value={config.enable_dedup ? 'true' : 'false'}
          onChange={(e) => onDedupChange(e.target.value === 'true')}
        >
          <option value="true">开启（默认）</option>
          <option value="false">关闭</option>
        </select>
        <p className="field-help">
          关闭后会抓取重复 URL（同一链接可被重复请求）；默认建议保持开启。
        </p>
      </div>
      <p className="field-help">
        并发数和下载延时会映射到框架 `CONCURRENCY` / `DOWNLOAD_DELAY` 设置。默认参数适合大多数站点。
      </p>
    </div>
  </section>
)
