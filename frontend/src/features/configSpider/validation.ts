import type { ConfigSpiderConfig } from './types'

function hasAtLeastOneUrl(config: ConfigSpiderConfig): boolean {
  return config.start_urls.some((url) => url.trim().length > 0)
}

function hasInvalidFieldRows(config: ConfigSpiderConfig): boolean {
  return config.fields.some((field) => {
    const hasName = field.name.trim().length > 0
    const hasSelector = field.selector.trim().length > 0
    return hasName !== hasSelector
  })
}

function hasInvalidAttr(config: ConfigSpiderConfig): boolean {
  return config.fields.some((field) => {
    const hasName = field.name.trim().length > 0
    const hasSelector = field.selector.trim().length > 0
    if (!hasName || !hasSelector) {
      return false
    }
    return field.attr.trim().length === 0
  })
}

function completeFieldCount(config: ConfigSpiderConfig): number {
  return config.fields.filter(
    (field) => field.name.trim().length > 0 && field.selector.trim().length > 0,
  ).length
}

export function validateBeforeRun(config: ConfigSpiderConfig): string | null {
  if (!hasAtLeastOneUrl(config)) {
    return '❌ 请至少填写一个起始 URL！'
  }
  if (hasInvalidFieldRows(config)) {
    return '❌ 字段行需同时填写“字段名”和“选择器”，或两者都留空。'
  }
  if (hasInvalidAttr(config)) {
    return '❌ 属性不能为空。若选择“自定义属性”，请填写属性名（如 title、data-id）。'
  }
  if (completeFieldCount(config) === 0) {
    return '❌ 请至少添加一个完整字段（字段名 + 选择器）。'
  }
  return null
}

export function validateBeforeTest(config: ConfigSpiderConfig): string | null {
  return validateBeforeRun(config)
}
