import type { ConfigSpiderConfig, FieldConfig } from './types'

function cleanText(value?: string | null): string {
  return (value ?? '').trim()
}

function normalizeField(field: FieldConfig): FieldConfig {
  return {
    ...field,
    name: cleanText(field.name),
    selector: cleanText(field.selector),
    attr: cleanText(field.attr) || 'text',
  }
}

export function normalizeConfigForSubmit(config: ConfigSpiderConfig): ConfigSpiderConfig {
  const startUrls = config.start_urls
    .map((url) => cleanText(url))
    .filter((url) => url.length > 0)

  const fields = config.fields
    .map(normalizeField)
    .filter((field) => field.name.length > 0 && field.selector.length > 0)

  return {
    ...config,
    target_name: cleanText(config.target_name) || 'config_spider',
    start_urls: startUrls,
    list_selector: cleanText(config.list_selector),
    detail_url_selector: cleanText(config.detail_url_selector) || null,
    next_page_selector: cleanText(config.next_page_selector) || null,
    fields,
    enable_dedup: Boolean(config.enable_dedup),
    concurrency: Number.isFinite(config.concurrency) ? Math.max(1, Math.floor(config.concurrency)) : 8,
    download_delay: Number.isFinite(config.download_delay) ? Math.max(0, config.download_delay) : 0,
    max_items:
      config.max_items === null || config.max_items === undefined
        ? null
        : Math.max(1, Math.floor(config.max_items)),
  }
}
