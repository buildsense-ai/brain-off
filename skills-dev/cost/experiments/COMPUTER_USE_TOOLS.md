# Computer Use 底层工具清单

## 感知工具 (Perception)

### 1. screenshot()
- 截取屏幕
- 返回图像数据

### 2. element_detection()
- 识别UI元素
- 标注位置和类型
- 返回：[{type: "button", text: "上传", bbox: [x,y,w,h]}]

### 3. ocr_text()
- 提取屏幕文字
- 用于理解内容

## 操作工具 (Action)

### 4. mouse_move(x, y)
- 移动鼠标到坐标

### 5. mouse_click(button="left")
- 点击鼠标

### 6. keyboard_type(text)
- 输入文字

### 7. keyboard_press(key)
- 按特殊键（Enter、Tab等）

### 8. scroll(direction, amount)
- 滚动页面

### 9. drag(from_x, from_y, to_x, to_y)
- 拖拽操作

## 高级操作 (Composed)

### 10. click_element(description)
- 组合：element_detection + mouse_click
- 例：click_element("上传按钮")

### 11. fill_input(field_name, value)
- 组合：找输入框 + 点击 + 输入

### 12. wait_for_element(description, timeout)
- 等待元素出现
