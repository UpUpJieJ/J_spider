export type SelectorType = 'css' | 'xpath'

export type FieldFromPage = 'list' | 'detail'

export type FieldScope = 'page' | 'node'

export interface FieldConfig {
  name: string
  selector: string
  attr: string
  from_page: FieldFromPage
  scope: FieldScope
}

export interface ConfigSpiderConfig {
  target_name: string
  start_urls: string[]
  selector_type: SelectorType
  list_selector: string
  detail_url_selector?: string | null
  next_page_selector?: string | null
  fields: FieldConfig[]
  enable_dedup: boolean
  concurrency: number
  download_delay: number
  max_items?: number | null
}

export interface TestResult {
  config_summary: Record<string, unknown>
  items: Array<Record<string, unknown>>
  total: number
}

export interface RunResult {
  items: Array<Record<string, unknown>>
  total: number
  message?: string
}
