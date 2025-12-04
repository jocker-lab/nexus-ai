/**
 * 兼容性模块 - 重新导出 DocumentList
 * @deprecated 请使用 DocumentList 替代
 */
'use client'

export { DocumentList, ReportList } from './DocumentList'
export default DocumentList

// 重新导出 DocumentList 作为默认导出
import { DocumentList } from './DocumentList'
