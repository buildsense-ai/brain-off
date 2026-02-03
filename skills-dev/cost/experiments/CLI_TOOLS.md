# CLI 底层工具清单

## 文件系统工具

### 1. read_file(path)
- 读取文件内容
- 支持文本、二进制

### 2. write_file(path, content)
- 写入文件

### 3. list_directory(path)
- 列出目录内容

### 4. find_files(pattern)
- 搜索文件
- 例：find_files("*.dwg")

### 5. file_exists(path)
- 检查文件是否存在

## 进程控制工具

### 6. bash(command)
- 执行shell命令
- 返回输出和状态码

### 7. run_background(command)
- 后台运行命令

### 8. kill_process(pid)
- 终止进程

## 网络工具

### 9. http_request(url, method, data)
- HTTP请求
- 支持GET/POST等

### 10. download_file(url, save_path)
- 下载文件

### 11. upload_file(url, file_path)
- 上传文件

## 数据处理工具

### 12. grep(pattern, text)
- 文本搜索

### 13. sed(pattern, replacement, text)
- 文本替换

### 14. parse_json(text)
- JSON解析

### 15. parse_xml(text)
- XML解析
