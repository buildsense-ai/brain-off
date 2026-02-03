#!/usr/bin/env python3
"""生成高清 CAD 图片"""

import sys
import os

# 导入转换函数
sys.path.insert(0, os.path.dirname(__file__))
exec(open('03_cad_to_image.py').read())

dxf_path = '/Users/zhuhanyuan/Desktop/甲类仓库建施.dxf'

# 1. 生成高清 PNG (600 DPI, 无尺寸限制)
print('=' * 60)
print('📸 生成高清 PNG (600 DPI)...')
print('=' * 60)
png_path = convert_dxf_to_image(
    dxf_path,
    output_path='/Users/zhuhanyuan/Desktop/甲类仓库建施_高清.png',
    max_size=None,  # 不限制尺寸
    dpi=600,
    output_format='png'
)

print()
print('=' * 60)
print('📄 生成矢量 PDF...')
print('=' * 60)
# 2. 生成矢量 PDF
pdf_path = convert_dxf_to_image(
    dxf_path,
    output_path='/Users/zhuhanyuan/Desktop/甲类仓库建施.pdf',
    max_size=None,
    dpi=150,  # PDF 不需要太高 DPI
    output_format='pdf'
)

print()
print('=' * 60)
print('✅ 完成！')
print('=' * 60)
print(f'PNG: {png_path}')
print(f'PDF: {pdf_path}')
