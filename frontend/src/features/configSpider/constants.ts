import type { ConfigSpiderConfig, FieldConfig } from './types'

export const emptyField = (): FieldConfig => ({
  name: '',
  selector: '',
  attr: 'text',
  from_page: 'list',
  scope: 'node',
})

export const defaultConfig: ConfigSpiderConfig = {
  target_name: 'config_spider',
  start_urls: [''],
  selector_type: 'css',
  list_selector: '',
  detail_url_selector: '',
  next_page_selector: '',
  fields: [emptyField()],
  enable_dedup: true,
  concurrency: 8,
  download_delay: 0,
  max_items: null,
}
