# Agent 分层工具架构设计

## 核心理念

**"捷径优先，基础兜底"**

当专业工具无法解决问题时，Agent可以使用最基本的工具自己思考Plan来解决。

---

## 三层架构

### Layer 1: 专家技能层 (Expert Skills)

**特点**：
- 封装人类专业经验
- 高效、精确
- 领域特定

**示例**：
```python
# 造价专家技能
cost_skill.calculate_wall_quantity(cad_file)
cost_skill.search_quota_standard(query)
cost_skill.export_boq_to_excel(plan_id)
```

**何时使用**：
- ✅ 有现成的专业工具
- ✅ 任务明确、标准化
- ✅ 需要高精度结果

---

### Layer 2: 通用能力层 (General Capabilities)

**特点**：
- 跨领域通用
- 中等复杂度
- 组合使用

**示例**：
```python
# 通用工具
file_ops.read_file(path)
web.search(query)
database.query(sql)
```

**何时使用**：
- ✅ 跨多个领域的任务
- ✅ 需要组合多个操作
- ✅ 没有专业工具但有通用方案

---

### Layer 3: 基础工具层 (Primitive Tools) ⭐

**特点**：
- 最底层、最灵活
- Agent自己规划使用
- 类似人类的基本能力

**分类**：

#### 3.1 Computer Use (视觉+操作)
```python
# 感知
screenshot()
detect_elements()
ocr_text()

# 操作
click(x, y)
type(text)
scroll(direction)
```

#### 3.2 CLI Tools (命令行)
```python
# 文件系统
bash("ls -la")
read_file(path)
find_files("*.dwg")

# 网络
http_request(url)
download_file(url)
```

**何时使用**：
- ✅ 没有现成工具
- ✅ 需要极致灵活性
- ✅ 一次性任务
- ✅ 探索性任务

---

## 决策流程

```
用户任务
    ↓
[检查] 有专家技能？
    ↓ Yes → 使用 Layer 1 (快速解决)
    ↓ No
[检查] 有通用工具？
    ↓ Yes → 使用 Layer 2 (组合解决)
    ↓ No
[使用] Layer 3 基础工具
    ↓
Agent 自己 Plan
    ↓
逐步执行基础操作
```

---

## 实际案例

### 案例1: DWG转换

**有API（Layer 1）**：
```python
# 1行搞定
convert_dwg_to_dxf(file_path, api_key)
```

**无API（Layer 3）**：
```python
# Agent自己Plan
1. screenshot()  # 看屏幕
2. open_browser("convertio.co")
3. click_element("上传按钮")
4. type(file_path)
5. click_element("转换")
6. wait_for_download()
```

---

### 案例2: 查询定额

**有数据库（Layer 1）**：
```python
search_quota_standard("240mm砖墙")
```

**无数据库（Layer 3）**：
```python
# Agent自己Plan
1. open_browser("定额查询网站")
2. fill_input("搜索框", "240mm砖墙")
3. click_element("搜索")
4. screenshot()
5. ocr_text()  # 提取结果
6. parse_and_save()
```

---

## 关键点

### 1. 元素检测的实现

你提到的问题很关键：

**方式A：坐标操作（原始）**
```python
click(x=100, y=200)  # 脆弱，界面变化就失效
```

**方式B：语义操作（智能）**
```python
click_element("上传按钮")  # 灵活，自动适应界面
```

**实现原理**：
```python
def click_element(description):
    # 1. 截屏
    img = screenshot()

    # 2. 视觉模型识别元素
    elements = vision_model.detect_ui_elements(img)
    # 返回：[{type:"button", text:"上传", bbox:[x,y,w,h]}]

    # 3. 匹配描述
    target = match_description(description, elements)

    # 4. 点击中心点
    click(target.center_x, target.center_y)
```

### 2. CLI的灵活性

CLI确实非常灵活：

```python
# 复杂的文件处理
bash("find . -name '*.dwg' | xargs -I {} dwg2dxf {}")

# 数据提取
bash("grep -r '定额' data/ | awk '{print $2}'")

# 网络操作
bash("curl -X POST api.com/convert -F file=@data.dwg")
```

**优势**：
- ✅ 组合能力强
- ✅ 生态丰富
- ✅ 性能好

---

## 总结

你的理解完全正确：

1. **专业工具是捷径** - 优先使用
2. **基础工具是兜底** - 保证灵活性
3. **Computer Use + CLI** - 两大基础能力
4. **Agent自己Plan** - 用基础工具组合解决问题

这就是现代AI Agent的核心架构！
