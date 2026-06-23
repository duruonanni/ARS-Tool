# Asset Recovery File Processing Assistant 说明与优化需求

## 1. 文档目的

本文档基于当前项目文件、业务交流记录和邮件说明整理，用于说明 Asset Recovery File Processing Assistant 的业务背景、现有功能、使用方式、输入输出要求、已知问题及 mentor 明确交代的短期优化需求。

当前工具定位为一个本地运行的小工具原型，帮助 LOT/运营团队在资产租赁到期回收流程中减少手工整理和查询工作。
短期目标是让业务团队先用起来并收集反馈；当前短期优化重点来自 mentor 的两点要求：一是优化产品查询速度和正确率，二是提升 Tab 1 对不同 input 文件格式的兼容性。中长期可以作为后续正式系统或业务系统集成项目的需求输入。

## 2. 业务背景

联想租赁业务中，客户租赁电脑、显示器、服务器等设备，通常有固定租期，例如 3 年。租期结束前，LOT需要提前与客户确认到期设备的处理方式：

- 续租或继续保留部分设备。
- 退回部分或全部到期设备。
- 如需退回，客户会提供或确认一份待退回资产清单。

每台设备都有唯一序列号 Serial Number，简称 SN。SN 用于定位具体设备；同一型号或同一 Part Number / Machine Type Model 下的多台设备通常具有相同或接近的硬件配置。

当客户确认设备退回后，LOT 需要基于客户确认的资产清单准备 Pick-up Request，并发给 Asset Recovery Services partner。ARS Partner 会根据 Pick-up Request 去客户现场回收设备，并基于设备信息进行后续报价、处置和回收流程。

目前人工流程的痛点在于：运营人员需要逐个 SN 到 Lenovo 支持/保修查询网站查询设备硬件规格，例如处理器、内存、硬盘、显卡等，再整理到 ARS Pick-up Request 模板中。该过程重复、耗时，且在设备数量较大时容易出错。

## 3. 当前项目概览

项目目录：`AI-Project/ASR`

关键文件：

- `Asset Recovery File Processing/ALM_to_ARS_Converter.html`
  - 前端单页网页工具。
  - 内嵌 SheetJS/JSZip，可在浏览器读取和生成 Excel。
  - 提供两个 Tab：Pick-up Request Generator、Recovery Status Analyzer。
- `Asset Recovery File Processing/lenovo_spec_server.py`
  - 本地 Python HTTP 服务。
  - 默认监听 `http://localhost:9527`。
  - 负责绕过浏览器 CORS 限制，查询 Lenovo 支持网站接口和产品页面，返回标准化硬件规格。
- `Asset Recovery File Processing/Start_Spec_Server.bat`
  - Windows 启动脚本。
  - 启动 Python 服务并打开浏览器。
- `Start_Spec_Server.command`
  - macOS 启动脚本。
  - 设计目标是启动 Python 服务并打开浏览器。
  - 注意：按当前目录结构，该脚本位于 `AI-Project/ASR` 根目录，但 `lenovo_spec_server.py` 位于 `Asset Recovery File Processing/` 子目录，脚本路径需要修正后才能稳定使用。
- `data/`
  - 当前收集到的样例文件，包括 ALM 导出、客户/业务清单样例、ARS Pick-up Request 样例。


| 文件 | 用途 | 适合丢进 Tab 1 吗 |
| --- | --- | --- |
| alm_hardware.xlsx | 标准/接近标准的 ALM hardware 导出样例，首个 Sheet 有 Display name、Serial number、Account | 适合现在测试 Tab 1|
| Minor Hotel - EOL notification...xlsx | 客户/业务实际清单样例，真正明细在 details Sheet，有 Part Number、Product Description、Serial Number | 适合测试优化后的格式兼容性；当前版本直接上传大概率识别不好，因为第一个 Sheet 是汇总表 |
| LFS - AsiaPac Technology Asset Details...xlsx | 大型多 Sheet EOL 资产清单，含多个明细 Sheet 和 Pivot Sheet，字段如 S/N、Material desc、Material Code、Customer name | 适合做压力测试和格式兼容性测试；当前版本直接上传大概率识别不好 |
| ARS Pick-up Request.xlsx | 已生成/目标格式的 Pick-up Request 样例 | 输出模板参考 / Tab 2 的 Pick-up Request 输入测试 |

## 4. 现有功能

### 4.1 Tab 1 - Pick-up Request Generator

目标：将客户/ALM 返回资产清单转换为 ARS Pick-up Request。

当前主要流程：

1. 用户上传待退回设备清单 `.xlsx`。
2. 工具读取 Excel 首个 Sheet，并解析资产数据。
3. 工具提取 SN、客户 Account、Model / Display name 等字段。
4. 工具按设备型号分组：
   - 优先使用 Machine Type Model。
   - 其次使用 Part Number / PN。
   - 最后使用 Model / Display name。
5. 工具基于 Model 自动识别 Product Type 和 Manufacturer。
6. 对 Lenovo 设备，工具自动调用本地 Python 服务查询硬件规格。
7. 查询结果填入 Product Details 表格，包括：
   - Processor Type and Size
   - Processor Quantity
   - Memory Type and Size
   - Memory Quantity
   - Drive Type
   - Drive Size
   - Drive Quantity
   - GPU Type and Size
   - GPU Quantity
   - Model Year
8. 用户补充 Overview 信息，例如：
   - Customer Account Name
   - Collection Country
   - Collection Address
   - Expected Collection Date
   - Currency
   - Logistics / Data Security / Special Services 等
9. 用户点击 Generate Pick-up Request，工具生成并下载 ARS Input Template `.xlsx`。

如果 Lenovo 自动查询失败，当前工具会提供 Paste Spec 方式：用户打开 Lenovo 支持页面，复制规格信息并粘贴到弹窗中，工具再尝试解析规格文本并填入表格。

### 4.2 Tab 2 - Recovery Status Analyzer

目标：对比已发出的 Pick-up Request 和 partner 回收确认清单，判断哪些设备已回收、哪些仍未回收。

当前主要流程：

1. 用户上传一个或多个 Pick-up Request 文件。
2. 用户上传一个或多个 Collection Report 文件。
3. 工具从所有文件中解析 SN、Model、Account、来源文件。
4. 工具对 Collection Report 建立 SN 确认映射。
5. 工具支持一定的 SN 归一化：
   - 原始 SN。
   - 自动补 `S` 前缀。
   - 对带首字母前缀的 SN 尝试去掉首字母匹配。
6. 工具生成结果表：
   - Total Devices Requested
   - Recovered
   - Not Yet Recovered
   - Recovery Rate
   - 每个 SN 的状态和确认来源文件
7. 用户可筛选 Recovered / Pending，也可以导出 Recovery Status Excel。

根据当前业务反馈，Tab 2 目前不是主要优化对象，整体可先保持现状。

## 5. 使用方式

### 5.1 前置条件

用户电脑需要安装 Python 3。

安装方式：

1. 前往 `https://www.python.org/downloads` 下载最新 Python 3。
2. Windows 安装时勾选 `Add Python to PATH`。
3. 安装完成后打开 Command Prompt，运行：

```bash
python --version
```

如果能看到版本号，则 Python 安装成功。

### 5.2 Windows 使用方式

1. 将以下文件放在同一个文件夹：
   - `ALM_to_ARS_Converter.html`
   - `lenovo_spec_server.py`
   - `Start_Spec_Server.bat`
2. 双击 `Start_Spec_Server.bat`。
3. 命令行窗口会启动本地服务，并打开浏览器访问：

```text
http://localhost:9527
```

4. 在网页中上传 Excel 并使用工具。
5. 使用完成后，关闭命令行窗口或按 `Ctrl+C` 停止服务。

注意：不要直接双击 HTML 文件打开。必须通过启动脚本打开，否则 Lenovo 规格查询能力可能不可用。

### 5.3 macOS 使用方式

当前项目根目录提供 `Start_Spec_Server.command`。

使用方式：

1. 双击 `Start_Spec_Server.command`，或在 Terminal 中执行。
2. 脚本会启动 Python 服务并打开：

```text
http://localhost:9527/
```

3. 使用完成后，在 Terminal 中按 `Ctrl+C` 停止服务。

当前 macOS 启动脚本位于 `AI-Project/ASR` 根目录，但 Python 服务文件位于 `Asset Recovery File Processing/` 子目录。后续需要确认该脚本在实际用户机器上的相对路径是否正确。

## 6. 输入与输出

### 6.1 Pick-up Request Generator 输入

理想输入是 ALM Hardware export 或客户确认后的资产清单 `.xlsx`。

当前代码主要依赖以下字段：

- SN 字段：
  - `Serial number`
  - `Serial Number`
  - `SN`
- Model 字段：
  - `Model`
  - `Display name`
- Account 字段：
  - `Account`
- 可选分组字段：
  - `Machine Type Model`
  - `MTM`
  - `Part Number`
  - `P/N`
  - `PN`

结合样例文件，真实业务中还会出现这些字段：

- `S/N `
- `Serial Number`
- `Part Number`
- `Product Description`
- `Material desc`
- `Customer name`
- `Legal Entity Name`
- `Brand`

业务上真正必要的最小字段是：

- SN / Serial Number：设备唯一标识。
- Model Name / Display Name / Product Description：设备型号或 PN 对应名称。
- 如有 Part Number / Machine Type Model，应优先用于分组和规格查询优化。

### 6.2 Pick-up Request Generator 输出

输出文件为 ARS Input Template `.xlsx`，当前下载命名类似：

```text
ARS_Template_{Account}_{YYYY-MM-DD}.xlsx
```

主要写入：

- Overview Sheet：客户名称、地址、国家、预计回收日期、币种等。
- Product Details Sheet：按型号/PN 汇总后的产品行和硬件规格。
- SN Sheet：全部待回收设备序列号。

### 6.3 Recovery Status Analyzer 输入

输入包括：

- Pick-up Request files：发给 partner 的待回收资产清单。
- Collection Report files：partner 实际收货后的确认清单。

支持多文件上传。

### 6.4 Recovery Status Analyzer 输出

网页结果：

- 总设备数。
- 已回收数。
- 未回收数。
- 回收率。
- 每个 SN 的匹配状态和确认来源。

导出文件：

```text
Recovery_Status_{YYYY-MM-DD}.xlsx
```

包含 Summary 和 Recovery Details 两个 Sheet。

## 7. 当前实现逻辑与限制

### 7.1 规格查询逻辑

当前 Lenovo 规格查询为两层实现：

1. 前端优先请求本地 Python 服务：

```text
GET http://localhost:9527/spec?sn={SN}
```

2. Python 服务查询 Lenovo 支持接口：
   - `getproducts?productId={SN}`
   - `getproductspec?productId={SN/productId/MTM}`
   - 产品 HTML 页面中的 Specification 表格

如果本地服务不可用，前端还会尝试浏览器侧 CORS proxy fallback，但可靠性较低。

### 7.2 查询性能限制

当前每个分组会拿该组内 SN 逐个尝试，直到某个 SN 返回规格为止。虽然已经按型号分组，但仍然依赖 SN 查询入口。

问题：

- 同一 PN / MTM 下的多台设备配置通常相同，没有必要逐台 SN 查询。
- SN 查询可能触发 Lenovo 网站限制、WAF 或接口不稳定。
- 当一个分组包含多个 SN 且前几个失败时，查询时间会明显变长。
- 当前 Python HTTP Server 是单线程 `HTTPServer`，大量查询时并发能力有限。
- 没有持久化缓存；同一型号下次上传仍需重新查询。

### 7.3 输入格式限制

Tab 1 当前只读取第一个 Sheet，并且表头识别偏固定。

样例显示真实文件可能存在：

- 多个 Sheet。
- 透视表/汇总表在前，真实明细表在后。
- SN 字段叫 `S/N ` 或 `Serial Number`。
- 型号字段叫 `Product Description`、`Material desc`，不一定叫 `Display name`。
- PN 字段叫 `Part Number`。
- 客户字段叫 `Customer name` 或 `Legal Entity Name`。
- 客户可能返回自定义格式，不按 ALM 标准导出模板。

因此现有 Tab 1 对非标准输入的兼容性不足。

### 7.4 用户体验限制

- 需要用户本地安装 Python，且必须通过启动脚本进入网页。
- 查询失败时错误原因不够明确，业务用户很难判断是网络、字段、SN、Lenovo 网站限制还是产品无规格。
- Product Details 表格较宽，字段多，业务用户需要横向滚动和手动检查。
- 自动查询进度为顺序处理，缺少更细的批量进度、耗时估计、失败列表和重试策略。

## 8. 优化需求

本节中的短期优化需求来自 mentor 交代，不是后续开发自行发散的优化建议。当前需要优先完成两点：

1. 优化产品查询的速度和正确率。
2. 优化 Tab 1 - Pick-up Request Generator 支持的 input 文件格式，使其更灵活。

### 8.1 P0 - 优化产品查询速度和正确率

背景：当前工具主要通过 SN（Serial Number）定位并查询 Lenovo 产品规格。这个方式在业务上不够高效，也不完全必要，因为同一 PN / Display name 对应的一批设备通常具有相同或接近的产品规格。逐个 SN 查询会导致速度慢、失败概率高，也容易受到 Lenovo 查询接口或网页限制影响。

目标：把查询策略从“逐个 SN 查询”优化为“优先利用 PN / Display name 分组查询”，减少重复查询次数，提高查询速度和结果正确率。

需求：

1. 输入解析时必须优先提取以下字段：
   - Serial Number / SN / S/N
   - PN / Display name
   - Model Name / Product Description
   - 如文件中存在 Part Number / Machine Type Model / MTM，也应一并识别并用于辅助分组
2. 查询分组逻辑应优先利用 PN / Display name：
   - 相同 PN / Display name 的设备归为一组。
   - 每组只需要查询一次产品规格。
   - 查询结果应用到该组全部 SN。
   - 只有当 PN / Display name 缺失或无法定位产品时，才回退到 SN 查询。
3. 查询正确率优化：
   - 对 PN / Display name 做标准化处理，例如去除多余空格、大小写差异、常见前后缀差异。
   - 查询结果需要和输入的 PN / Display name / Model 做基本匹配校验，避免查到错误型号。
   - 对查询失败的组保留失败原因，方便用户重试或手动补充规格。
4. 增加缓存，减少重复访问 Lenovo 查询接口：
   - `pn/displayName -> spec`
   - `modelName -> spec`
   - `sn -> product metadata`
5. 可选增加本地持久化缓存：
   - JSON 文件缓存查询结果。
   - 缓存命中时无需访问 Lenovo 网站。
6. Python 服务可新增更明确的查询 API：

```text
GET /spec?sn={SN}
GET /spec?pn={PN}
GET /spec?displayName={DISPLAY_NAME}
POST /spec/batch
```

7. 对批量查询设置合理并发和限速：
   - 避免并发过高触发 Lenovo WAF。
   - 建议按组查询，并发 3-5 个组，失败后退避重试。
8. 查询失败时返回结构化错误：
   - product not found
   - spec not found
   - network timeout
   - blocked by Lenovo/WAF
   - invalid input

验收标准：

- 同一 PN / Display name 的多台设备只发起一次规格查询。
- 100 台设备、10 个 PN / Display name 分组的清单，应按 10 组左右完成查询，而不是按 100 个 SN 查询。
- 查询失败后用户能看到失败原因，并能一键重试或手工 Paste Spec。

### 8.2 P0 - 优化 Tab 1 输入文件格式兼容性

背景：Tab 1 - Pick-up Request Generator 的输入文件不一定都是标准 ALM 导出格式。客户或业务团队可能提供不同模板、不同 Sheet、不同列名的 Excel。mentor 明确要求这个功能支持的 input 文件格式更灵活，只要文件里包含 SN 和 PN / Display name 等关键字段，就应尽量识别出来。

目标：提升 Tab 1 对不同 input 文件格式的兼容性。只要用户上传文件中存在 SN 和 PN / Display name / Model 信息，工具就能识别并处理；如果自动识别失败，应允许用户手动映射字段继续使用。

需求：

1. Tab 1 不应只读第一个 Sheet，应扫描所有 Sheet。
2. 自动跳过明显的汇总/说明 Sheet，例如：
   - pivot summary
   - overview
   - definitions
   - read me
   - status meaning
3. 自动选择最可能的明细 Sheet：
   - 包含 SN 字段。
   - 包含 PN / Display name / Model / Description 字段。
   - 数据行数量较多。
4. 表头识别支持更多别名：
   - SN：`Serial number`、`Serial Number`、`SN`、`S/N`、`S/N `、`Asset SN`、`Manuf. SN`
   - PN / Display name：`Display name`、`Part Number`、`PN`、`P/N`、`Material Code`
   - Model：`Model`、`Model Name`、`Product Description`、`Material desc`、`Description`
   - MTM：`Machine Type Model`、`MTM`
   - Account：`Account`、`Customer name`、`Legal Entity Name`、`Company`
   - Brand：`Brand`、`Make`
5. 支持用户在自动识别失败时手动映射字段：
   - 选择 SN 列。
   - 选择 Model/Description 列。
   - 选择 PN/MTM 列。
   - 选择 Account 列。
6. 对识别结果提供预览：
   - 识别到的 Sheet 名。
   - 识别到的字段映射。
   - 资产总数。
   - 有效 SN 数。
   - 分组数。
   - 前 10 行样例。
7. 对空 SN、重复 SN、异常 SN 给出提示，不应静默丢弃。

验收标准：

- 标准 ALM 导出可以识别。
- 客户自定义清单只要包含 SN + PN / Display name / Model / Description，也可以识别。
- 多 Sheet 文件可以自动找到明细 Sheet。
- 自动识别失败时，用户可通过手动映射继续。

### 8.3 P1 - 优化 UI 流程

目标：让业务用户更容易理解当前状态、定位问题并完成输出。

建议：

1. 上传后先进入字段识别预览页，再进入 Product Details。
2. 查询状态按组展示：
   - Pending
   - Querying
   - Done
   - Failed
   - Cached
   - Manual
3. 增加失败汇总区：
   - 哪些组查询失败。
   - 失败原因。
   - Retry All Failed。
   - Paste Spec。
4. Product Details 表格增加冻结关键列或更紧凑视图：
   - Model / PN
   - Qty
   - Spec Status
5. 增加导出前校验：
   - 必填 Overview 是否完整。
   - Product Details 是否还有空关键字段。
   - SN 数量是否与分组数量汇总一致。
6. 增加用户可读的完成提示：
   - 已生成文件名。
   - 写入多少 SN。
   - 写入多少产品分组。

### 8.4 P1 - 增强 Recovery Status Analyzer

虽然当前第二个功能不是优先优化对象，但后续可考虑：

1. 复用 Tab 1 的字段识别逻辑，提升 Collection Report 兼容性。
2. 支持更多 SN 归一化规则，并把原始 SN 和归一化 SN 都展示出来。
3. 对只出现在 Collection Report 但不在 Pick-up Request 中的 SN 单独列为 Extra Received。
4. 对重复 SN、跨文件重复、一个 SN 多状态等异常生成 Exception Report。
5. 导出结果增加 Pending-only Sheet，方便运营继续跟进。

### 8.5 P2 - 部署和系统集成

短期工具是本地离线原型；后续可考虑部署到 Lenovo Web Server 或对接业务系统。

建议方向：

1. 部署为内部 Web 应用，免去用户本地安装 Python。
2. 后端统一处理 Excel 解析、规格查询、缓存、文件生成。
3. 与 ALM / 租赁业务系统对接，自动读取到期资产清单。
4. 与客户确认流程对接，减少手动上传客户反馈清单。
5. 与 ARS partner 交互流程对接，自动追踪 Pick-up Request、Collection Report 和报价状态。

## 9. 建议优先级

第一阶段，聚焦 mentor 交代的两点短期优化：

1. 优化产品查询速度和正确率：从逐个 SN 查询调整为优先利用 PN / Display name 分组查询。
2. 优化 Tab 1 input 文件格式兼容性：支持更多模板、更多 Sheet、更多字段命名，并提供字段映射兜底。

第二阶段，增强业务闭环：

1. Recovery Status Analyzer 异常报告。
2. 更好的导出校验。
3. 用户反馈收集。

第三阶段，产品化：

1. 内部 Web 部署。
2. 权限、日志、审计。
3. 与 ALM/租赁/ARS 流程系统集成。

## 10. 邮件说明建议版本

可用于发送给测试用户的简化说明：

---

Attached is a local prototype tool to assist the Asset Recovery process.

What it does:

- Pick-up Request Generator: upload a returned asset list `.xlsx`; the tool groups devices by model/PN, looks up Lenovo hardware specs, and generates an ARS Pick-up Request template.
- Recovery Status Analyzer: upload Pick-up Request files and Collection Reports; the tool compares serial numbers and generates a recovery status summary.

Before using it, please install Python 3 from `https://www.python.org/downloads`. On Windows, please make sure `Add Python to PATH` is checked during installation.

Getting started:

1. Save `ALM_to_ARS_Converter.html`, `lenovo_spec_server.py`, and `Start_Spec_Server.bat` in the same folder.
2. Double-click `Start_Spec_Server.bat`.
3. Your browser should open `http://localhost:9527`.
4. Upload your Excel file and follow the steps on the page.
5. When finished, close the Command Prompt window or press `Ctrl+C`.

Please do not open the HTML file directly, because the Lenovo spec lookup requires the local Python helper server.

Feedback requested:

- Does the tool open and run without issues?
- Can it recognize your asset list format?
- Are Lenovo specs returned correctly?
- Are any fields or workflow steps unclear?
- Please share any failed sample files so we can improve format compatibility.
