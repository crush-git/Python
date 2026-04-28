# Stage 1 单文件截图替换：subagent 标准 prompt 模板

> 控制器派出 subagent 处理 1 个 markdown 文件时，把这份模板内容（包括所有"硬规则"）+ 当前文件信息组合成 prompt 发给 subagent。

---

## 你的任务

把 markdown 文件 `<FILE_PATH>` 中的所有 `![](http*)` 外链图片引用，根据图本身内容（已下载到 `_legacy_images/<对应路径>/`）转换为合适的 markdown 元素：

- **代码截图** → ```python 代码块（小写 python）
- **运行输出截图** → 不带语言标记的 ``` 输出块
- **表格截图** → markdown 表格
- **流程图/概念图** → 文字描述 + ASCII 图 / Mermaid（可选）
- **完全无法识别或图损坏** → 按上下文重写一段等价文字，并在 commit message 中注明

完成后：
1. 确认文件中无 `![](http*)` 残留
2. 跑 `python3 tools/example_runner.py <文件所在目录>` 让 ```python 块跑通
3. `git add <文件>` + `git commit` 用简洁中文 message

---

## 硬规则（必须遵守）

### 0. 防卡死规则（最重要）

**若 Read 一张图返回 API 错误**（特别是 `Could not process image` / 400 等）：
- **绝对不要重试**该图（重试会再次触发同样错误，浪费时间）
- **绝对不要继续读其它图**（先处理这张图再继续）
- **立即 fallback**：跳过该图，根据上下文（图前后段落）写一段合理的等价代码块或文字
- 在 commit message 注明哪张图按上下文重写

**若 Read 一张图前先用 Bash `file <path>` 确认是合法 PNG/JPEG/GIF/WebP**——如果 `file` 输出 `ASCII text` 或非图片类型，**不要 Read**，直接 fallback 按上下文重写，并在 commit message 注明文件已损坏。

### 1. 风格守则（详见 spec §4）

- 段落短，3-5 行就分段；自问自答的句式保留
- 「两点水/做鸭事业部/产品反馈」等招牌情境**绝不替换**为通用例子
- 全角中文标点；中英之间留半角空格
- 反引号包代码标识符 `like_this`，「方括号」包概念词
- 代码块**几乎不写注释**（解释靠前后段落）
- ```python 用小写

### 2. 只动该文件 + 只动图位置

- **不修改原文段落文字**（除非该位置就是图替换）
- **不订正过期语法**（`.format()` → f-string 是 Plan 2 的事，本任务不做）
- **不改章节标题、目录路径、文件名**

### 3. 单文件原子化提交

- 处理完整个文件后**一次 commit**（不要边改边 commit）
- commit message 格式：`<目录>/<文件>：截图转代码块`
- 若有 fallback 重写，附加一行说明：`其中第 N 张图按上下文重写（原图损坏 / API 拒绝）`

### 4. 验证

- commit 前必跑 `python3 tools/example_runner.py <文件所在目录>`，所有该文件的 ```python 块必须 PASS（输出代码块除外，因为不是 python 块）
- 若某段确实需要演示语法错误或依赖外部资源（如 SMTP），代码块前加 `<!-- skip-ci -->` 单行注释跳过 CI

### 5. 状态报告

完成后向控制器报告：

```
DONE
- 处理了 N 张图：M 张转代码块，K 张转输出块，L 张转表格，X 张 fallback 重写（原因）
- example_runner: 该目录全部 PASS
- commit SHA: <sha>
```

如果任一步骤失败：

```
BLOCKED
- 卡在哪一步: ...
- 错误信息: ...
- 我已经做的: ...
```

---

## 工作流（按顺序执行）

```
1. Read <FILE_PATH> 全文
2. grep -n '!\[' <FILE_PATH> 列出所有图位置（含上下文行号）
3. 对每张图：
   a. ls -la 对应 _legacy_images/.../<图文件名>
   b. file 命令验证是合法图片
   c. 若是合法图片 → Read 识别 → 转 markdown
      若是 ASCII text 或缺失 → 跳过图，按上下文重写
4. Edit/Write 修改 <FILE_PATH>，逐张替换 ![](http...) 行
5. python3 tools/example_runner.py <文件所在目录> 验证
6. git add + git commit
7. 报告 DONE
```

---

## 当前任务参数（控制器填）

- `<FILE_PATH>`：（具体文件路径）
- 图数：（grep 统计的图数）
- 当前 commit 起点：（HEAD SHA）
