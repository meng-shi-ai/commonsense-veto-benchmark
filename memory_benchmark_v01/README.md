# Memory Evidence Benchmark v0.1

**A synthetic diagnostic pilot for deciding which remembered facts still apply.**

这是第一版可运行研究原型，使用描述性名称 Memory Evidence Benchmark。
核心问题：助手不仅要记得过去说过什么，还要分清信息属于谁、是谁确认的、何时有效，以及后来的信息有没有真正推翻它。

**当前状态：数据集、提示词导出、模型接入接口、评分器和测试已完成；尚未运行任何真实模型评测。**
`validation/` 里的分数全部来自人工标签或固定程序输出，只用于检查软件，不能放进模型排行榜。

## 先看一个例子

过去助手说：“你可以选 SOC 210。”后来用户说：“我在考虑这门课。”
问题：用户现在选上这门课了吗？

答案应当是“现有信息不足”，不能把推荐、考虑或助手自己的推测写成已选课。
配对案例只把后来那句话改成“我已经正式注册了 SOC 210”，正确答案就必须变成“已选上”。

也有反方向的控制案例：用户明确说“以后默认简短回复，直到我改口”，半年没有更新，
模型应该保留这条偏好，不能仅仅因为时间过去就说不知道。

## 这 24 个案例测什么

| Family | Cases | What should change the answer? |
|---|---:|---|
| Explicit update | 4 | Moving home versus merely visiting; changing versus retaining a preference |
| Durable versus temporary | 4 | A standing preference versus a dated, expired instruction |
| Suggestion versus commitment | 4 | Considering a course/purchase versus confirming it |
| Correction and provenance | 4 | User correction; a stale generated summary versus a fresh user statement |
| Subject attribution | 4 | The user versus a roommate/coworker, including quoted first-person speech |
| Authorization scope | 4 | Draft versus send; retained versus revoked permission |

共 12 对；每对只改一个事件的一项字段（文本或说话者）。18 个案例可确定答案，6 个信息不足。
所有案例是原创合成内容，借鉴已讨论的失误类型，使用虚构地点、课程和产品。
它们不是从私人对话导出的真实数据，也不是已证明在模型上发生的 24 次失败。

## 在 Mac 上运行

下载解压后，在 Terminal 里进入 `memory_benchmark_v01` 文件夹。需要 Python 3.9 或更新版本；无第三方依赖。

```bash
python3 benchmark.py validate
python3 -m unittest -v
python3 benchmark.py demo --out demo_report.json
```

前三条命令都不调用模型、不需要 API key。`demo` 只检验评分器。

### 今晚不想碰代码：也能手动测

打开 `example_prompt.txt`，在一个新的聊天里，把整个文件发给要测的模型。
它对应案例 C010。输出是一个很短的 JSON，用来区分答案、证据和信息不足。
这个例子的参考答案在 `gold.jsonl` 中；不要把该文件发给被测模型。

不要在已经看过答案的当前聊天里测试再把结果当作独立评测。界面产品如果开启了额外记忆，
请记录这一点；它与没有外部记忆的 API 设置不是同一种实验条件。

## 完整评测

### 方式 A：导出提示词，收集模型回答

```bash
python3 benchmark.py export --split all --out prompts.jsonl
```

每行含 `id` 和 `messages`。对每个案例开启独立上下文，发送对应的两个 messages，
不要加入 `gold.jsonl`、配对标签或前一个案例的答案。

将输出保存为 JSONL，每行形式如下（仅格式示例，不是某一案例的参考答案）：

```json
{"id":"C001","prediction":{"decision":"answer","value":"Riverton","evidence_ids":["E1"]}}
```

然后评分：

```bash
python3 benchmark.py score --predictions predictions.jsonl --out report.json
```

### 方式 B：用你自己的模型适配器

```bash
python3 benchmark.py run --adapter "python3 your_adapter.py" --out predictions.jsonl
python3 benchmark.py score --predictions predictions.jsonl --out report.json
```

适配器从 stdin 读取一条 `{"id":...,"messages":[...]}`，从 stdout 返回纯 JSON prediction。
runner 每个案例启动一次独立进程，不传前例输出，不传标签；适配器内部如果另有持久状态，需自行关闭并记录。
日志只能写 stderr。非零退出、超时、非 JSON 返回均记录为错误，不跳过失败案例、不自动重试。
已有输出文件会阻止覆盖。用新的文件名开始下一次运行。

包内 `adapter_http.py` 是一个可选的 chat-completions 风格 HTTP 接口适配器：

- `BENCHMARK_ENDPOINT`：服务提供方的完整接口 URL。
- `BENCHMARK_MODEL`：你实际可访问的模型 ID。
- `BENCHMARK_API_KEY`：如服务需要，放在环境变量中。
- `BENCHMARK_EXTRA_BODY`：可选 JSON 对象，用于该服务支持的采样或输出长度设置。

```bash
python3 benchmark.py run --adapter "python3 adapter_http.py" --limit 1 --out smoke_predictions.jsonl
```

设置上述环境变量后才可运行。这会向所配置的服务发送请求，可能产生费用；本交付未执行这种调用。
该适配器只支持返回 `choices[0].message.content` 的服务，不是各家原生 API 的通用适配器。
没有自动重试或重定向；严格 JSON 输出失败照常计入错误，不悄悄修复。
先小规模验证服务兼容性，再去掉 `--limit`。单例 smoke 输出不能当成完整评测。

## 输出与评分

模型只能返回 `decision`、`value`、`evidence_ids` 三个字段：

- `decision="answer"`：`value` 必须是当前案例 `allowed_values` 里的精确字符串。
- `decision="clarify"`：`value=null`。表示该问题的信息不足，不意味着真实产品里必须打断用户。
- `evidence_ids`：支持该判断的事件 ID；未知答案也要指出相关但不足以确定的证据。

| Metric | Definition |
|---|---|
| State accuracy | Valid schema, correct decision and value / all selected cases |
| Evidence accuracy | Valid schema and exact match to one acceptable minimal evidence set / all cases |
| Strict accuracy | State and evidence both correct / all cases |
| Pair strict accuracy | Both members strictly correct / all selected pairs |
| Macro family strict accuracy | Unweighted average of the six family strict accuracies |
| Unnecessary clarification | Valid clarify outputs / all answerable cases |
| Unsupported answer | Valid answer outputs / all unknown cases |
| Coverage and schema validity | Returned records and valid predictions / all selected cases |

缺失或格式错误的回答，在准确率分母里照样保留。未知 ID 或重复 ID 直接报错。
行为错误率只统计格式有效的错误，所以必须和 coverage/schema validity 一起报告；
例如一个全部崩溃的系统可能显示零行为错误，但准确率也是零，不能解释为安全。

`State accuracy` 与 `Strict accuracy` 应并列报告：证据集合的人工标注可能不唯一，
不要把引用集合的格式敏感性误当成语义理解失败。当前 gold 给出最小证据集合；
如果经人工复核发现另一个充分集合，应在固定版本之前统一补充，不能只为某个模型临时放宽。

## 文件

| File | Purpose |
|---|---|
| `cases.jsonl` | Model-visible case data; no labels |
| `gold.jsonl` | Evaluator-only labels, families, pairs, splits, annotation reasons |
| `build_dataset.py` | Reproducible case authoring source; not for model input |
| `benchmark.py` | Validation, prompt export, adapter execution, scoring and fixture demo |
| `adapter_http.py` | Optional HTTP service adapter; no model or credentials selected |
| `test_benchmark.py` | Checks missing records, invalid outputs, evidence, pairs, and label separation |
| `fixture_adapter.py` | Fixed-output plumbing check; not a language model |
| `example_prompt.txt` | One ready-to-paste model input |
| `DESIGN.md` | Research scope, limitations, literature and next experiment |
| `validation/` | Software validation artifacts, explicitly not model results |

## 实验记录

开发与 pilot 各 12 题，每个 family 各一对；同一对不跨 split。
这是公开且相似的小型诊断集，`pilot` 不等于独立、隐藏、无污染的测试集。
调完提示词后再创建新的未见模板和场景，才能评估泛化。

至少记录：精确模型版本、服务/接口、时间、提示词与数据哈希、采样设置、
最大输出长度、额外记忆状态、模型是否见过样例/标签、运行次数、失败和重试策略。
run 生成的 metadata 只覆盖其中一部分，不能替代完整实验记录。

**这版能测短上下文中的记忆证据判断，还不能证明一个真实系统半年后的持久记忆可靠。**
更完整的研究设计见 `DESIGN.md`。
