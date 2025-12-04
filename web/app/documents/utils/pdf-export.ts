import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

interface ExportOptions {
  filename?: string
  onProgress?: (progress: number) => void
}

export async function exportToPDF(
  elementId: string,
  options: ExportOptions = {}
): Promise<void> {
  const { filename = 'report.pdf', onProgress } = options

  try {
    // 获取要导出的元素
    const element = document.getElementById(elementId)
    if (!element) {
      throw new Error('Element not found')
    }

    onProgress?.(10)

    // 使用html2canvas将DOM转换为Canvas
    // 不修改原始元素，所有修改在克隆文档中进行
    const canvas = await html2canvas(element, {
      scale: 2, // 提高清晰度
      useCORS: true, // 支持跨域图片
      logging: false,
      backgroundColor: '#ffffff',
      windowWidth: 1280, // 固定宽度，匹配max-w-7xl
      onclone: (clonedDoc) => {
        // 在克隆的文档中查找对应元素
        const clonedElement = clonedDoc.getElementById(elementId)
        if (clonedElement) {
          // 只修改克隆元素的样式
          clonedElement.style.width = '210mm'
          clonedElement.style.maxWidth = '210mm'
          clonedElement.style.padding = '20mm'
        }

        // 移除固定定位的元素（如进度条、导航）
        const fixedElements = clonedDoc.querySelectorAll('.fixed, [style*="position: fixed"]')
        fixedElements.forEach((el) => el.remove())

        // 移除目录导航和进度条
        const toc = clonedDoc.querySelector('[class*="xl:block fixed"]')
        if (toc) toc.remove()

        // 优化打印样式
        const style = clonedDoc.createElement('style')
        style.innerHTML = `
          * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          .glass-card, .glass-content, .glass-sidebar {
            background: #ffffff !important;
            backdrop-filter: none !important;
            border: 1px solid #e2e8f0 !important;
          }
          .animated-gradient-bg {
            background: #ffffff !important;
          }
          body {
            background: #ffffff !important;
          }
        `
        clonedDoc.head.appendChild(style)
      },
    })

    onProgress?.(70)

    // 创建PDF
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    })

    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pdfHeight = pdf.internal.pageSize.getHeight()
    const imgWidth = canvas.width
    const imgHeight = canvas.height
    const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight)

    const imgX = (pdfWidth - imgWidth * ratio) / 2
    const imgY = 0

    // 计算需要的页数
    const pageCount = Math.ceil((imgHeight * ratio) / pdfHeight)

    onProgress?.(80)

    // 添加页面
    for (let i = 0; i < pageCount; i++) {
      if (i > 0) {
        pdf.addPage()
      }

      const yOffset = -(i * pdfHeight)
      pdf.addImage(
        imgData,
        'PNG',
        imgX,
        yOffset,
        imgWidth * ratio,
        imgHeight * ratio
      )

      onProgress?.(80 + (20 * i) / pageCount)
    }

    onProgress?.(95)

    // 保存PDF
    pdf.save(filename)

    onProgress?.(100)
  } catch (error) {
    console.error('PDF export error:', error)
    throw error
  }
}

// 导出为图片
export async function exportToImage(
  elementId: string,
  filename: string = 'report.png'
): Promise<void> {
  try {
    const element = document.getElementById(elementId)
    if (!element) {
      throw new Error('Element not found')
    }

    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff',
    })

    // 转换为Blob并下载
    canvas.toBlob((blob) => {
      if (!blob) return

      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
    })
  } catch (error) {
    console.error('Image export error:', error)
    throw error
  }
}
