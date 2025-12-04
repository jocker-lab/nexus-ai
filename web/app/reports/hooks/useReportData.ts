/**
 * 兼容性模块 - 重新导出 useDocumentData
 * @deprecated 请使用 @/app/documents/hooks/useDocumentData 替代
 */
'use client'

export { useReportData } from '@/app/documents/hooks/useDocumentData'
export type { Report, UseReportDataReturn } from '@/app/documents/hooks/useDocumentData'
