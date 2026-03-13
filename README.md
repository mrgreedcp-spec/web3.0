# Web3.0 转行学习计划（前两个月详细版）

> 本计划面向有一定编程基础（如前端/后端开发经验）、希望系统转入 Web3.0 领域的开发者。
> 每天预计投入 **3–4 小时**（工作日）/ **6–8 小时**（周末）。
> 状态标记：✅ 已完成 / 🔄 进行中 / ⬜ 待开始

---

## 第一个月：区块链与以太坊基础

### 第一周（Day 1–7）：区块链核心概念

| 日期 | 学习主题 | 具体任务 | 状态 |
|------|----------|----------|------|
| Day 1 | 区块链原理入门 | 1. 阅读《区块链：从数字货币到信用社会》第1章<br>2. 观看 3Blue1Brown《But how does bitcoin actually work?》视频<br>3. 整理笔记：什么是区块链、哈希函数、链式结构 | ⬜ |
| Day 2 | 共识机制 | 1. 学习 PoW（工作量证明）与 PoS（权益证明）原理<br>2. 阅读 Ethereum.org 官方文档《Consensus mechanisms》<br>3. 用自己的语言写一段 200 字对比说明 | ⬜ |
| Day 3 | 去中心化网络 | 1. 学习 P2P 网络基础<br>2. 了解节点类型（全节点、轻节点、矿工节点）<br>3. 本地安装 Geth（以太坊客户端），观察日志输出 | ⬜ |
| Day 4 | 钱包与密钥管理 | 1. 学习公钥/私钥加密原理（椭圆曲线 secp256k1）<br>2. 安装 MetaMask，创建测试钱包<br>3. 在 Goerli 测试网领取测试 ETH（faucet）<br>4. 理解助记词（BIP-39）的生成机制 | ⬜ |
| Day 5 | 交易与手续费 | 1. 学习以太坊交易结构（nonce、gasPrice、gasLimit、data 字段）<br>2. 在 Etherscan 上分析 3 笔真实交易<br>3. 用 MetaMask 在测试网发送一笔转账，观察 Gas 费用 | ⬜ |
| Day 6 | 第一周总结 & 刷题 | 1. 复习本周所有笔记<br>2. 完成 Ethereum.org 上的《Blockchain fundamentals》测验<br>3. 在 GitHub 创建学习仓库，提交本周笔记（Markdown 格式） | ⬜ |
| Day 7 | 休息 & 扩展阅读 | 1. 阅读《The Infinite Machine》（以太坊诞生故事）第1–3章<br>2. 浏览 Ethereum roadmap（ethereum.org/en/roadmap），了解未来方向 | ⬜ |

---

### 第二周（Day 8–14）：以太坊深入 & 开发工具链

| 日期 | 学习主题 | 具体任务 | 状态 |
|------|----------|----------|------|
| Day 8 | 以太坊账户模型 | 1. 区分 EOA（外部账户）与合约账户<br>2. 学习以太坊状态树（MPT 默克尔帕特里夏树）概念<br>3. 阅读 EIP-1559（伦敦升级）手续费改革文档 | ⬜ |
| Day 9 | 开发环境搭建 | 1. 安装 Node.js（LTS）、npm/yarn<br>2. 安装 Hardhat：`npm install --save-dev hardhat`<br>3. 运行 `npx hardhat` 创建示例项目，跑通默认测试<br>4. 安装 VS Code 插件：Solidity（Juan Blanco） | ⬜ |
| Day 10 | Hardhat 工作流 | 1. 学习 Hardhat 本地节点（`npx hardhat node`）<br>2. 学习编译、部署、测试命令<br>3. 阅读官方文档《Hardhat Runner》教程并完成全部示例 | ⬜ |
| Day 11 | Remix IDE 入门 | 1. 打开 remix.ethereum.org，熟悉界面<br>2. 使用 Remix 编译并部署第一个 Hello World 合约到 JavaScript VM<br>3. 调用合约函数，观察返回值与事件日志 | ⬜ |
| Day 12 | Foundry 工具链 | 1. 安装 Foundry（`curl -L https://foundry.paradigm.xyz | bash`）<br>2. 学习 `forge init`、`forge build`、`forge test` 命令<br>3. 对比 Hardhat vs Foundry 的优缺点，写一篇短文 | ⬜ |
| Day 13 | 第二周综合练习 | 1. 用 Hardhat 部署一个简单 ERC-20 Token 到测试网<br>2. 用 Etherscan 验证合约（verify）<br>3. 整理工具链使用笔记并提交到 GitHub | ⬜ |
| Day 14 | 休息 & 社区参与 | 1. 注册并浏览 ETHGlobal Discord<br>2. 阅读 Week in Ethereum News 最新一期<br>3. 关注 5 个 Web3 开发者 Twitter/X 账户（如 @PatrickAlphaC、@transmissions11） | ⬜ |

---

### 第三周（Day 15–21）：Solidity 基础语法

| 日期 | 学习主题 | 具体任务 | 状态 |
|------|----------|----------|------|
| Day 15 | Solidity 数据类型 | 1. 学习基本类型：`uint`、`int`、`bool`、`address`、`bytes`<br>2. 学习引用类型：`string`、`array`、`struct`、`mapping`<br>3. 在 Remix 中编写练习合约，测试每种类型 | ⬜ |
| Day 16 | 函数与修饰符 | 1. 学习函数可见性（`public`/`private`/`internal`/`external`）<br>2. 学习状态可变性（`pure`/`view`/`payable`）<br>3. 编写一个包含各类修饰符的合约并运行测试 | ⬜ |
| Day 17 | 控制流与错误处理 | 1. 学习 `if/else`、`for`、`while`、`do-while`<br>2. 掌握 `require`、`revert`、`assert` 的使用场景与区别<br>3. 学习自定义错误（Custom Errors，Solidity ≥0.8.4）节省 Gas | ⬜ |
| Day 18 | 继承与接口 | 1. 学习合约继承（`is` 关键字）、`override`/`virtual`<br>2. 学习 `interface` 与 `abstract contract`<br>3. 实现一个简单的多继承示例（钻石问题的 Solidity 解决方案） | ⬜ |
| Day 19 | 事件与日志 | 1. 学习 `event` 声明与 `emit` 触发<br>2. 理解 `indexed` 参数的作用（便于过滤）<br>3. 用 Hardhat 测试监听事件，用 `ethers.js` 查询历史日志 | ⬜ |
| Day 20 | Gas 优化基础 | 1. 学习存储槽（storage slot）布局与 packing 优化<br>2. 对比 `memory` 与 `storage` 的 Gas 成本<br>3. 用 `forge snapshot` 测量并比较优化前后 Gas 差异 | ⬜ |
| Day 21 | 休息 & 小项目 | 1. 独立实现一个简单的投票合约（Voting Contract）<br>2. 编写 Hardhat 单元测试覆盖所有函数<br>3. 将代码推送到 GitHub 并写好 README | ⬜ |

---

### 第四周（Day 22–30）：ERC 标准与 DeFi 基础概念

| 日期 | 学习主题 | 具体任务 | 状态 |
|------|----------|----------|------|
| Day 22 | ERC-20 标准 | 1. 精读 EIP-20 原文<br>2. 阅读 OpenZeppelin ERC20 实现源码<br>3. 用 OpenZeppelin 库实现自定义代币（包含 mint/burn/transfer） | ⬜ |
| Day 23 | ERC-721 NFT 标准 | 1. 精读 EIP-721 原文<br>2. 阅读 OpenZeppelin ERC721 实现<br>3. 部署一个 NFT 合约到测试网，用 MetaMask 查看 NFT | ⬜ |
| Day 24 | ERC-1155 多代币标准 | 1. 学习 EIP-1155 与 ERC-721 的区别（批量转账、Gas 效率）<br>2. 实现一个简单的游戏道具合约（ERC-1155）<br>3. 编写测试用例 | ⬜ |
| Day 25 | OpenZeppelin 安全库 | 1. 学习 `Ownable`、`AccessControl`、`Pausable` 模块<br>2. 学习 `ReentrancyGuard` 防重入攻击<br>3. 将 Day 22–24 的合约重构为使用 OZ 安全库 | ⬜ |
| Day 26 | DeFi 核心概念 | 1. 学习 AMM（自动做市商）原理：x×y=k 公式<br>2. 阅读 Uniswap V2 白皮书（核心机制部分）<br>3. 在 Uniswap 测试网进行一次 Swap 操作，观察滑点 | ⬜ |
| Day 27 | 借贷协议原理 | 1. 学习超额抵押借贷（Aave/Compound 机制）<br>2. 理解利率模型（借贷利率曲线）<br>3. 阅读 Aave V3 文档中的《How it works》章节 | ⬜ |
| Day 28 | 预言机（Oracle） | 1. 学习链上/链下数据问题（Oracle Problem）<br>2. 了解 Chainlink 价格预言机的工作原理<br>3. 在 Remix 中编写一个调用 Chainlink ETH/USD 价格馈送的合约 | ⬜ |
| Day 29 | 第一月综合复习 | 1. 回顾 Day 1–28 的所有笔记<br>2. 重新完成投票合约（加入 ERC-20 投票权重）<br>3. 整理一份"第一月学习总结"博客文章并发布到 GitHub Pages 或 Mirror.xyz | ⬜ |
| Day 30 | 休息 & 规划 | 1. 评估第一月完成情况，标记每日状态<br>2. 调整第二月计划（根据薄弱环节补强）<br>3. 浏览 ETHGlobal 黑客松项目列表，选定感兴趣的赛道 | ⬜ |

---

## 第二个月：智能合约开发实战 & DApp 构建

### 第五周（Day 31–37）：高级 Solidity & 合约安全

| 日期 | 学习主题 | 具体任务 | 状态 |
|------|----------|----------|------|
| Day 31 | 重入攻击（Reentrancy） | 1. 学习重入攻击原理，复现 DAO 攻击过程<br>2. 在 Hardhat 中编写可被攻击的合约与攻击合约<br>3. 用 `ReentrancyGuard` 修复，跑通测试 | ⬜ |
| Day 32 | 整数溢出与下溢 | 1. 学习 Solidity <0.8 的溢出问题与 SafeMath<br>2. 理解 Solidity ≥0.8 的内置溢出检查<br>3. 完成 Ethernaut Level 1（Fallback）& Level 2（Fallout）CTF | ⬜ |
| Day 33 | 访问控制漏洞 | 1. 学习 `tx.origin` vs `msg.sender` 攻击<br>2. 完成 Ethernaut Level 4（Telephone）<br>3. 学习正确的权限控制模式（Role-based Access Control） | ⬜ |
| Day 34 | 闪电贷攻击原理 | 1. 学习闪电贷（Flash Loan）工作流程<br>2. 阅读经典闪贷攻击案例（bZx 攻击分析）<br>3. 用 Aave V3 接口实现一个无套利的闪贷示例合约 | ⬜ |
| Day 35 | 合约升级模式 | 1. 学习代理模式（Proxy Pattern）：透明代理 vs UUPS<br>2. 用 OpenZeppelin Upgrades 插件部署可升级合约<br>3. 实践升级流程：部署 V1 → 添加功能 → 升级到 V2 | ⬜ |
| Day 36 | 静态分析工具 | 1. 安装并运行 Slither：`pip install slither-analyzer`<br>2. 对自己的合约跑 Slither 分析，修复所有 High/Medium 告警<br>3. 了解 Mythril、Echidna 模糊测试工具 | ⬜ |
| Day 37 | 休息 & 安全审计练习 | 1. 完成 Ethernaut Level 6（Delegation）& Level 7（Force）<br>2. 阅读 Trail of Bits 安全博客一篇<br>3. 将本周安全笔记整理并提交 GitHub | ⬜ |

---

### 第六周（Day 38–44）：前端集成 — ethers.js & wagmi

| 日期 | 学习主题 | 具体任务 | 状态 |
|------|----------|----------|------|
| Day 38 | ethers.js 基础 | 1. 安装 ethers.js v6：`npm install ethers`<br>2. 学习 Provider / Signer / Contract 三大核心类<br>3. 用脚本查询账户余额、调用合约只读函数 | ⬜ |
| Day 39 | ethers.js 写操作 | 1. 编写脚本发送 ETH 转账<br>2. 调用合约状态变更函数（send transaction）<br>3. 监听合约事件（`contract.on("EventName", callback)`） | ⬜ |
| Day 40 | React + MetaMask 连接 | 1. 用 `create-react-app` 或 `vite` 初始化前端项目<br>2. 集成 MetaMask 连接（`window.ethereum`）<br>3. 显示已连接账户地址和 ETH 余额 | ⬜ |
| Day 41 | wagmi + RainbowKit | 1. 安装 wagmi v2 和 RainbowKit<br>2. 配置多链支持（Ethereum Mainnet + Goerli）<br>3. 用 `useReadContract` / `useWriteContract` 替换原生 ethers.js 调用 | ⬜ |
| Day 42 | The Graph 数据索引 | 1. 阅读 The Graph 官方文档《Quick Start》<br>2. 为 Day 22 的 ERC-20 合约部署 Subgraph（到 The Graph Studio）<br>3. 用 GraphQL 查询代币 Transfer 事件历史 | ⬜ |
| Day 43 | IPFS & 去中心化存储 | 1. 了解 IPFS 内容寻址原理（CID）<br>2. 用 Pinata 上传 NFT 元数据（JSON + 图片）<br>3. 将 IPFS URI 设置为 NFT tokenURI，在 OpenSea 测试网查看效果 | ⬜ |
| Day 44 | 休息 & 前端集成练习 | 1. 将 Day 22 的 ERC-20 合约与 React 前端打通（铸币、转账、余额查询）<br>2. 部署前端到 Vercel<br>3. 写一篇集成总结文章 | ⬜ |

---

### 第七周（Day 45–51）：完整 DApp 开发实战

| 日期 | 学习主题 | 具体任务 | 状态 |
|------|----------|----------|------|
| Day 45 | 项目选题 & 架构设计 | 1. 确定实战项目方向（推荐：去中心化众筹平台）<br>2. 设计智能合约接口（函数、事件、数据结构）<br>3. 画出前端页面草图（3–4 个页面） | ⬜ |
| Day 46 | 合约开发（第一阶段） | 1. 编写 `Crowdfunding.sol` 核心逻辑（创建项目、捐款、退款）<br>2. 编写 Hardhat 单元测试（≥80% 覆盖率）<br>3. 在本地网络部署并手动测试 | ⬜ |
| Day 47 | 合约开发（第二阶段） | 1. 添加时间锁（`block.timestamp` 截止日期）<br>2. 实现多签提款功能<br>3. 补充测试用例，确保边界条件覆盖 | ⬜ |
| Day 48 | 合约安全审查 | 1. 用 Slither 扫描众筹合约<br>2. 人工 Review：检查重入、溢出、访问控制<br>3. 修复发现的问题并记录安全决策 | ⬜ |
| Day 49 | 前端开发（第一阶段） | 1. 搭建 React + wagmi 项目骨架<br>2. 实现"项目列表"与"创建项目"页面<br>3. 连接合约：展示链上项目数据 | ⬜ |
| Day 50 | 前端开发（第二阶段） | 1. 实现"捐款"功能（写操作 + Loading 状态 + Toast 通知）<br>2. 实现"退款"功能（条件判断 + 错误处理）<br>3. 移动端响应式适配（Tailwind CSS） | ⬜ |
| Day 51 | 休息 & 代码整理 | 1. 代码 Review，重构命名与注释<br>2. 补充 README（项目介绍、本地运行步骤、截图）<br>3. 提交到 GitHub，整理 PR | ⬜ |

---

### 第八周（Day 52–60）：部署上线 & 求职准备

| 日期 | 学习主题 | 具体任务 | 状态 |
|------|----------|----------|------|
| Day 52 | 测试网完整部署 | 1. 将众筹合约部署到 Sepolia 测试网<br>2. 在 Etherscan 验证合约源码（Hardhat verify 插件）<br>3. 前端环境变量切换为 Sepolia，测试完整流程 | ⬜ |
| Day 53 | 多链适配 | 1. 学习 Polygon（PoS）网络配置<br>2. 将合约部署到 Mumbai 测试网（Polygon 测试网）<br>3. 前端增加网络切换按钮，支持 Ethereum + Polygon | ⬜ |
| Day 54 | Layer 2 入门 | 1. 学习 Optimistic Rollup（Optimism/Arbitrum）原理<br>2. 将合约部署到 Arbitrum Goerli<br>3. 对比 L1 vs L2 的 Gas 费用差异（记录数据） | ⬜ |
| Day 55 | 项目压力测试 | 1. 编写 Hardhat 脚本模拟 100 笔并发交易<br>2. 测试边界条件（零地址、最大金额、截止时间边界）<br>3. 记录并修复发现的问题 | ⬜ |
| Day 56 | 作品集准备 | 1. 整理 GitHub Profile README（突出 Web3 项目）<br>2. 为众筹项目录制 3 分钟 Demo 视频（用 Loom）<br>3. 将项目发布到 Mirror.xyz 写成案例文章 | ⬜ |
| Day 57 | 简历与求职材料 | 1. 更新简历，突出 Solidity / ethers.js / Hardhat 技能栈<br>2. 准备 5 道常见 Web3 面试题的书面回答<br>3. 在 LinkedIn 更新技能标签（Solidity、DeFi、Smart Contracts） | ⬜ |
| Day 58 | 开源贡献 | 1. 在 GitHub 上找一个活跃的 Web3 开源项目（如 OpenZeppelin）<br>2. 提交一个 Good First Issue 的 PR 或文档修复<br>3. 参与项目 Discord 讨论 | ⬜ |
| Day 59 | 黑客松准备 | 1. 报名最近一期 ETHGlobal 或本地区 Web3 黑客松<br>2. 组建或寻找队友（1–2 人）<br>3. 预研黑客松赛题方向，头脑风暴产品点子 | ⬜ |
| Day 60 | 两个月总结 & 规划 | 1. 回顾并标记 Day 1–60 全部完成情况<br>2. 统计输出成果：合约数量、GitHub commits、文章数量<br>3. 制定第三个月计划（深入 DeFi / NFT / Layer2 专项）<br>4. 在社区分享两个月学习心得 | ⬜ |

---

## Web3.0 赛道调研与收益分析（2020–2026）

> ⚠️ **免责声明**：以下内容为公开市场信息的整理与分析，仅供学习参考，**不构成任何投资建议**。加密市场波动极大，请务必自行研究（DYOR）并评估风险。

---

### 一、RWA（Real World Assets / 现实世界资产代币化）

#### 什么是 RWA？
RWA 是将传统金融中的现实资产（如美国国债、房地产、企业债、大宗商品等）通过区块链代币化，使其可以在链上自由交易、借贷和组合的赛道。

#### 发展时间线

| 年份 | 关键事件 | 市场规模（TVL） |
|------|----------|----------------|
| 2020 | MakerDAO 开始接受 RWA 作为抵押品；Centrifuge 推出 Tinlake 平台 | ~$1 亿 |
| 2021 | Centrifuge 融资 $900 万；Goldfinch 上线新兴市场信贷池 | ~$5 亿 |
| 2022 | 美联储加息，链上美债收益吸引力飙升；MakerDAO RWA 占其收入 >50% | ~$15 亿 |
| 2023 | BlackRock 推出 BUIDL 基金（代币化美国国债）；Ondo Finance 爆发增长；RWA TVL 突破 $50 亿 | ~$50 亿 |
| 2024 | Franklin Templeton、UBS 等传统巨头入场；Centrifuge 与 Aave 合作；链上美债超 $20 亿 | ~$120 亿 |
| 2025 | RWA 被视为本轮牛市核心叙事之一；私人信贷、房地产、碳信用代币化加速 | ~$200 亿+ |
| 2026（预测） | 机构级 RWA 基础设施成熟；跨链 RWA 互通；监管框架逐步明确 | 预计 $500 亿+ |

#### 代表项目与表现

| 项目 | 代币 | 赛道 | 2023 初→2025 峰值涨幅 | 简介 |
|------|------|------|----------------------|------|
| Ondo Finance | ONDO | 代币化美债 | ~10x–15x | 短期美国国债代币化，TVL 最高超 $6 亿 |
| Centrifuge | CFG | 企业信贷 | ~3x–5x | 最早的 RWA 协议之一，与 MakerDAO/Aave 深度合作 |
| Maple Finance | MPL | 机构借贷 | ~5x–8x | 面向机构的无抵押/低抵押链上借贷 |
| Goldfinch | GFI | 新兴市场信贷 | ~2x–4x | 向新兴市场实体企业提供链上贷款 |
| Pendle Finance | PENDLE | 收益代币化 | ~20x–50x | 将收益（yield）代币化交易，2023–2024 爆发 |
| Polymesh | POLYX | 合规证券链 | ~2x–3x | 专为合规证券代币设计的 L1 链 |

**RWA 赛道特点**：
- ✅ 有真实收益支撑（如美债 4–5% 年化），非纯投机
- ✅ 传统金融巨头入场（BlackRock、Franklin Templeton）带来合法性
- ✅ 监管友好度最高的 DeFi 赛道
- ⚠️ 代币价格增长空间相对 Meme/GameFi 较有限，但稳定性最强

---

### 二、自行发币（Token Launch）模式分析

#### 主要发币方式对比

| 方式 | 典型年份 | 代表案例 | 平均投入成本 | 潜在收益 | 风险等级 |
|------|----------|----------|-------------|----------|----------|
| **ICO**（首次代币发行） | 2017–2018 | Ethereum, EOS, Filecoin | 中（$5K–$50K） | 极高（早期项目 10x–1000x） | 🔴 极高 |
| **IEO**（交易所首发） | 2019–2020 | BitTorrent, Matic | 中（需交易所合作费） | 高（3x–50x） | 🟡 高 |
| **IDO**（去中心化首发） | 2020–2021 | 通过 Polkastarter/DAO Maker | 低（$1K–$10K） | 高（5x–100x） | 🟡 高 |
| **Fair Launch**（公平启动） | 2020–至今 | Yearn (YFI), Sushi | 极低（仅 Gas 费） | 极高（YFI：$0→$40,000） | 🟡 中高 |
| **Meme 代币** | 2021–至今 | DOGE, SHIB, PEPE, WIF | 极低 | 极高/极低（1000x 或归零） | 🔴 极高 |
| **Launchpad 平台** | 2021–至今 | Binance Launchpad | 中（需持有平台币） | 中（2x–10x） | 🟢 中 |
| **pump.fun 一键发币** | 2024–2025 | Solana 生态 Meme 币 | 极低（<$10） | 极端不确定 | 🔴 极高 |
| **代币化 AI Agent** | 2024–2026 | Virtuals Protocol, ai16z | 中 | 高（10x–100x） | 🟡 高 |

#### 发币的真实收益数据（代表性案例）

| 案例 | 发行方式 | 初始市值 | 峰值市值 | 最高 ROI | 当前状态 |
|------|----------|----------|----------|----------|----------|
| YFI (2020) | Fair Launch | ~$0 | ~$16 亿 | ∞（无初始成本） | 活跃，TVL 稳定 |
| SHIB (2020) | 社区发行 | ~$0 | ~$400 亿 | 数百万倍 | 活跃但远离峰值 |
| PEPE (2023) | Meme | ~$0 | ~$70 亿 | 数十万倍 | 波动剧烈 |
| WIF (2023) | Meme (Solana) | ~$0 | ~$40 亿 | 数万倍 | 波动剧烈 |
| ONDO (2024) | 机构+社区 | ~$2 亿 | ~$30 亿 | ~15x | 稳步上升 |

**关键结论**：
- 🎰 Meme 代币 ROI 最高但失败率 >99%，绝大多数归零
- 🏦 RWA/DeFi 代币收益较稳定（5x–20x），适合长期布局
- 🛠️ 作为开发者，**为他人/项目方提供发币技术服务**（合约开发、审计、前端）是风险最低且持续的收入方式

---

### 三、2020–2026 各赛道 ROI 排行

#### 赛道级别收益对比（基于赛道头部项目中位数表现）

| 排名 | 赛道 | 代表代币 | 2020–2025 中位 ROI | 说明 |
|------|------|----------|-------------------|------|
| 🥇 1 | **Meme 代币** | SHIB, PEPE, WIF, BONK | 100x–100,000x（但 99% 归零） | 极端高回报但极端高风险，不可复制 |
| 🥈 2 | **AI × Web3** | FET, RNDR, TAO, VIRTUAL | 20x–100x | 2023–2025 最强叙事，AI 算力+Agent 代币化 |
| 🥉 3 | **Layer 2 / 模块化** | ARB, OP, STRK, TIA | 5x–30x | 基础设施扩容，空投造富效应显著 |
| 4 | **RWA** | ONDO, PENDLE, CFG, MPL | 5x–50x | 真实收益支撑，机构资金入场 |
| 5 | **DePIN**（去中心化物理基础设施） | HNT, RNDR, FIL, IOTX | 3x–20x | 将硬件/物理网络代币化，长期叙事 |
| 6 | **DeFi 蓝筹** | UNI, AAVE, MKR, CRV | 2x–10x | 成熟赛道，收益率递减但最稳定 |
| 7 | **GameFi / 元宇宙** | AXS, SAND, IMX, GALA | -50%–5x | 2021 高峰后大幅回撤，等待 AAA 游戏破局 |
| 8 | **NFT** | CryptoPunks, BAYC, Azuki | -70%–3x | 2021–2022 高峰后大幅下跌，市场转冷 |

---

### 四、AI 时代 Web3.0 / 4.0 最赚钱的方向

#### 🏆 Top 5 最具盈利潜力方向（2025–2028）

**第 1 名：AI Agent × DeFi（AI 自主交易代理）**
- 💰 预计市场规模：2028 年 $500 亿+
- 📌 核心逻辑：让 AI Agent 自主执行链上交易（DeFi 策略、MEV 套利、跨链桥接）
- 🔧 开发者机会：
  - 构建 AI Agent 框架（如 ElizaOS、AutoGPT + Web3 插件）
  - 开发 Agent-to-Agent 支付协议
  - 为 AI Agent 构建链上身份（DID）和钱包管理系统
- 📊 代表项目：Virtuals Protocol (VIRTUAL)、ai16z (AI16Z)、Autonolas (OLAS)
- ⭐ **开发者年收入潜力：$15 万–$50 万+**

**第 2 名：RWA 基础设施开发**
- 💰 预计市场规模：2028 年 $10 万亿（传统资产上链）
- 📌 核心逻辑：帮助传统金融机构将资产代币化（国债、房地产、股权、基金）
- 🔧 开发者机会：
  - 合规代币化智能合约开发（ERC-3643 安全代币标准）
  - KYC/AML 链上合规解决方案
  - 机构级 RWA 管理平台前后端开发
- 📊 代表项目：Ondo, Centrifuge, Securitize, Backed Finance
- ⭐ **开发者年收入潜力：$12 万–$40 万**

**第 3 名：DePIN（去中心化物理基础设施网络）**
- 💰 预计市场规模：2028 年 $3,000 亿
- 📌 核心逻辑：用代币激励构建物理基础设施（GPU 算力、无线网络、传感器、存储）
- 🔧 开发者机会：
  - 去中心化 GPU 算力市场（AI 模型训练/推理）
  - IoT 设备链上注册与数据验证
  - 矿工/节点运营商激励合约
- 📊 代表项目：Render (RNDR)、Helium (HNT)、io.net、Hivemapper
- ⭐ **开发者年收入潜力：$10 万–$35 万**

**第 4 名：链上 AI 模型训练与推理市场**
- 💰 预计市场规模：2028 年 $1,000 亿
- 📌 核心逻辑：去中心化 AI 训练（联邦学习 + 区块链验证）、模型即资产（NFT 化模型权重）
- 🔧 开发者机会：
  - 构建去中心化推理网络（如 Bittensor 子网）
  - AI 模型 NFT 市场（训练权、使用权、收益权分离）
  - 隐私计算（ZKP + AI）基础设施
- 📊 代表项目：Bittensor (TAO)、Ritual、Gensyn、Modulus
- ⭐ **开发者年收入潜力：$12 万–$45 万**

**第 5 名：ZK（零知识证明）应用开发**
- 💰 预计市场规模：2028 年 $500 亿
- 📌 核心逻辑：用零知识证明实现隐私交易、可验证计算、身份验证
- 🔧 开发者机会：
  - ZK-Rollup 应用开发（zkSync、StarkNet 生态）
  - ZK 身份验证（Worldcoin、Polygon ID 生态）
  - ZK-ML（可验证 AI 推理）
- 📊 代表项目：zkSync (ZK)、StarkNet (STRK)、Aztec、Mina (MINA)
- ⭐ **开发者年收入潜力：$15 万–$60 万（ZK 开发者极度稀缺）**

---

### 五、给转行者的综合建议

#### 💡 最优策略路径（风险 vs 回报平衡）

```
短期收入（0–6 月）：
  → 学习 Solidity + Hardhat → 接 Web3 外包/兼职（合约开发、审计辅助）
  → 预期月收入：$2,000–$8,000

中期定位（6–18 月）：
  → 选择一个垂直方向深扎（推荐 AI Agent / RWA）
  → 加入一个成长期项目团队（远程全职或 DAO 贡献者）
  → 预期年收入：$80,000–$200,000

长期复利（18 月+）：
  → 建立个人品牌（Twitter/X、Mirror、GitHub 影响力）
  → 参与协议治理 / 获取代币激励 / 成为协议核心贡献者
  → 预期年收入：$150,000–$500,000+（含代币激励）
```

#### ⚡ 2025–2026 当下最值得 ALL-IN 的技能组合

| 优先级 | 技能 | 原因 |
|--------|------|------|
| ⭐⭐⭐ | **Solidity + 合约安全** | Web3 开发基础，所有方向都需要 |
| ⭐⭐⭐ | **AI Agent 框架（LangChain/ElizaOS + Web3）** | 2025 年最火的交叉赛道 |
| ⭐⭐ | **Rust（Solana/Cosmos 生态）** | 高性能链开发，薪资天花板高 |
| ⭐⭐ | **ZK 电路开发（Circom/Noir）** | 开发者极度稀缺，薪资最高 |
| ⭐ | **全栈 DApp（React + wagmi + The Graph）** | 求职面最广，项目数量最多 |

---

## AI 工程师入行技能图谱与作品集指南

> 本节回答：想转行 AI 工程师，需要哪些技能？完成什么项目可以证明自己的 AI 能力？

### 一、AI 工程师核心技能栈

#### 🧱 基础层（必备，0–3 个月掌握）

| 技能 | 具体要求 | 推荐学习资源 |
|------|----------|-------------|
| **Python 编程** | 熟练掌握 Python 3.10+，熟悉 OOP、装饰器、异步编程 | [Python 官方教程](https://docs.python.org/3/tutorial/) |
| **数学基础** | 线性代数（矩阵运算）、概率统计、微积分（梯度下降） | [3Blue1Brown 线性代数](https://www.3blue1brown.com/topics/linear-algebra)、[Khan Academy 概率统计](https://www.khanacademy.org/math/statistics-probability) |
| **机器学习基础** | 监督/无监督/强化学习概念，经典算法（线性回归、决策树、SVM、KNN） | [Andrew Ng - Machine Learning Specialization](https://www.coursera.org/specializations/machine-learning-introduction)（免费旁听） |
| **深度学习框架** | PyTorch（首选）或 TensorFlow，能搭建 CNN/RNN/Transformer | [fast.ai Practical Deep Learning](https://course.fast.ai/)（免费） |
| **数据处理** | Pandas、NumPy、Matplotlib/Seaborn 数据分析与可视化 | [Kaggle Learn](https://www.kaggle.com/learn) |

#### 🔧 工程层（进阶，3–6 个月掌握）

| 技能 | 具体要求 | 推荐学习资源 |
|------|----------|-------------|
| **LLM 应用开发** | 掌握 OpenAI API / Claude API / 本地模型（Ollama）、Prompt Engineering | [OpenAI Cookbook](https://cookbook.openai.com/)、[Anthropic Docs](https://docs.anthropic.com/) |
| **RAG 系统** | 向量数据库（Pinecone/Weaviate/ChromaDB）、文档分块、检索增强生成 | [LangChain RAG 教程](https://python.langchain.com/docs/tutorials/rag/) |
| **AI Agent 框架** | LangChain / LangGraph / CrewAI / AutoGen 多代理系统 | [DeepLearning.AI Short Courses](https://www.deeplearning.ai/short-courses/) |
| **模型微调** | LoRA / QLoRA 微调、Hugging Face Transformers、PEFT 库 | [Hugging Face Course](https://huggingface.co/course)（免费） |
| **MLOps 基础** | Docker 容器化、模型部署（FastAPI/BentoML）、CI/CD、模型监控 | [Made With ML](https://madewithml.com/) |

#### 🚀 专精层（高级，6–12 个月）

| 技能 | 具体要求 | 推荐学习资源 |
|------|----------|-------------|
| **AI × Web3 交叉** | 链上 AI Agent、去中心化推理（Bittensor）、ZK-ML | 本文档「AI 时代 Web3 最赚钱方向」章节 |
| **多模态 AI** | 图像+文本+音频模型（CLIP、Whisper、GPT-4V 集成） | [Hugging Face Multimodal](https://huggingface.co/docs/transformers/tasks/multimodal) |
| **分布式训练** | DeepSpeed / FSDP / Ray，大模型训练/推理优化 | [DeepSpeed 文档](https://www.deepspeed.ai/) |

---

### 二、证明 AI 能力的 5 类项目作品集

> 💡 建议至少完成 **3 个项目**，涵盖不同类型，全部开源在 GitHub 并配详细 README。

#### 项目 1：端到端 ML 项目（证明基础能力）
- **示例**：房价预测 / 客户流失分析 / 情感分析
- **要求**：数据清洗 → EDA → 特征工程 → 模型训练 → 评估 → 部署为 API
- **技术栈**：Python + Pandas + scikit-learn + FastAPI + Docker
- **亮点**：在 Kaggle 上获得 Top 10% 排名

#### 项目 2：LLM 应用（证明当下最热门能力）
- **示例**：智能客服机器人 / 个人知识库问答 / 代码审查助手
- **要求**：接入 LLM API + RAG + 向量数据库 + 前端界面
- **技术栈**：LangChain + ChromaDB + Streamlit/Gradio + OpenAI API
- **亮点**：处理真实场景，有对话记忆和引用来源

#### 项目 3：AI Agent 系统（证明前沿能力）
- **示例**：自动化研究助理 / 多 Agent 协作写作 / AI 交易策略 Agent
- **要求**：Agent 能自主规划、调用工具、反思和迭代
- **技术栈**：LangGraph / CrewAI + 工具调用 + 记忆系统
- **亮点**：展示 Agent 决策过程日志和效果对比

#### 项目 4：模型微调项目（证明深度能力）
- **示例**：特定领域客服模型 / 法律/医疗文本分类 / 多语言翻译微调
- **要求**：在 Hugging Face 预训练模型上 LoRA 微调 + 评估 + 发布
- **技术栈**：Hugging Face Transformers + PEFT + Weights & Biases
- **亮点**：发布到 Hugging Face Hub，写模型卡片（Model Card）

#### 项目 5：AI × Web3 跨界项目（证明独特竞争力）
- **示例**：AI 驱动的链上交易分析器 / NFT 智能估价工具 / DeFi 收益优化 Agent
- **要求**：AI 模型 + 区块链数据集成 + 可视化前端
- **技术栈**：Python + ethers.js/web3.py + The Graph + LLM API
- **亮点**：结合两个领域的稀缺交叉能力

---

### 三、能证明 AI 能力的认证与成就

| 类型 | 具体内容 | 难度 | 影响力 |
|------|----------|------|--------|
| **Kaggle 竞赛** | 获得 Expert 以上称号（至少 1 枚银牌/金牌） | ⭐⭐⭐ | 🔥🔥🔥 |
| **Hugging Face 发布** | 发布微调模型或数据集（被社区引用） | ⭐⭐ | 🔥🔥🔥 |
| **开源贡献** | 向 LangChain / Transformers / FastAPI 等贡献 PR | ⭐⭐⭐ | 🔥🔥🔥🔥 |
| **技术博客** | 在 Medium / dev.to / 个人站发布 AI 深度文章（≥5 篇） | ⭐ | 🔥🔥 |
| **DeepLearning.AI 证书** | 完成 Andrew Ng 的 ML/DL Specialization | ⭐⭐ | 🔥🔥 |
| **AWS/GCP ML 认证** | AWS ML Specialty / GCP Professional ML Engineer | ⭐⭐⭐ | 🔥🔥🔥 |
| **黑客松获奖** | ETHGlobal / Devpost / MLH 黑客松获奖 | ⭐⭐ | 🔥🔥🔥🔥 |

---

## 丹麦 vs 加拿大：AI 与 Web3 工程师就业市场分析

> 本节针对希望在 **丹麦** 或 **加拿大** 转行 AI / Web3 工程师的求职者。

### 一、两国 AI vs Web3 岗位需求对比（2025–2026）

| 维度 | 🇩🇰 丹麦 | 🇨🇦 加拿大 |
|------|----------|------------|
| **AI 工程师需求** | ⭐⭐⭐⭐ 旺盛 — 制药（Novo Nordisk）、能源（Vestas/Ørsted）、金融科技（Danske Bank）大量招聘 AI/ML 岗位 | ⭐⭐⭐⭐⭐ 极旺盛 — 多伦多/蒙特利尔是北美 AI 中心（Mila/Vector Institute），加上 Cohere、Ada、Shopify 等本土 AI 公司 |
| **Web3 工程师需求** | ⭐⭐ 一般 — Web3 公司较少，主要集中在柏林/阿姆斯特丹（但远程岗位可覆盖） | ⭐⭐⭐ 中等 — Ethereum Foundation 有加拿大成员，Consensys/Polygon 有远程岗，温哥华/多伦多有小型 Web3 Hub |
| **签证友好度** | ⭐⭐⭐ 工作许可（Arbejdstilladelse）需雇主担保，快速通道（Fast-track scheme）适用于 IT 岗 | ⭐⭐⭐⭐⭐ Express Entry / Global Talent Stream 对 IT 人才极友好，PR 路径清晰 |
| **平均年薪（AI）** | DKK 550,000–850,000（约 €74K–€114K / $80K–$125K） | CAD $90,000–$160,000（约 $65K–$120K USD） |
| **平均年薪（Web3）** | 远程为主，通常按美元计价 $80K–$200K（取决于协议/DAO） | 同上，远程为主 $80K–$200K |
| **生活成本** | 高（哥本哈根租房 DKK 8,000–12,000/月） | 中高（多伦多 CAD $1,800–$2,500/月，蒙特利尔更低） |
| **语言要求** | 英语通用（但丹麦语加分），AI 岗位通常纯英语 | 英语（蒙特利尔需法语加分） |
| **AI 生态成熟度** | ⭐⭐⭐ — 哥本哈根大学 AI 研究强，Pioneer Centre for AI | ⭐⭐⭐⭐⭐ — 全球顶级 AI 研究（Hinton/Bengio/Sutton），CIFAR、Mila、Vector、Amii |

### 二、结论：哪个行业更缺人？

```
📊 整体判断：

1. AI 工程师 >>> Web3 工程师（两国都更缺 AI 人才）
   - AI 岗位数量远多于 Web3（据 LinkedIn/Indeed 2025 年搜索结果估算，"AI Engineer" 相关岗位约为 "Web3/Solidity" 岗位的 5–10 倍）
   - AI 有传统企业（制药、金融、制造）的大量需求，Web3 主要局限于 Crypto Native 公司
   - AI 薪资更稳定（固定工资），Web3 薪资波动大（含代币部分）

2. 如果选 AI：加拿大 > 丹麦（岗位更多、签证更友好、AI 生态更成熟）
3. 如果选 Web3：两国差异不大（Web3 以远程为主，地理位置影响较小）
4. 最优策略：以 AI 为主业 + Web3 为副业/投资方向
```

### 三、30 天转型行动计划（AI 工程师方向）

> 目标：30 天内建立可展示的 AI 能力，为投递丹麦/加拿大 AI 工程师岗位做准备。

#### 第 1 周（Day 1–7）：基础补齐 + 环境搭建

| 日 | 任务 | 产出 |
|----|------|------|
| Day 1 | 1. 安装 Python 3.11+、VS Code、Git<br>2. 创建 GitHub 求职专用仓库（AI-Portfolio）<br>3. 注册 Kaggle、Hugging Face、LinkedIn 账号 | GitHub 仓库上线 |
| Day 2 | 1. 复习 Python 核心：列表推导式、装饰器、OOP<br>2. 完成 [Kaggle Python 微课程](https://www.kaggle.com/learn/python) | Kaggle 证书截图 |
| Day 3 | 1. 复习 NumPy + Pandas 核心操作<br>2. 完成 [Kaggle Pandas 微课程](https://www.kaggle.com/learn/pandas) | Kaggle 证书截图 |
| Day 4 | 1. 学习 scikit-learn 基础（分类/回归/评估指标）<br>2. 完成 [Kaggle Intro to ML](https://www.kaggle.com/learn/intro-to-machine-learning) | Kaggle 证书截图 |
| Day 5 | 1. 学习 PyTorch 基础（张量、自动微分、nn.Module）<br>2. 跟着 [PyTorch 60min Blitz](https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html) 完成练习 | 练习代码提交 GitHub |
| Day 6 | 1. 开始 Kaggle 入门竞赛（Titanic 或 House Prices）<br>2. 完成 EDA + 基线模型提交 | 首次 Kaggle 提交 |
| Day 7 | 1. 优化 Kaggle 竞赛分数（特征工程 + 集成模型）<br>2. 写一篇完整的比赛分析笔记（Kaggle Notebook） | Notebook 发布 |

#### 第 2 周（Day 8–14）：LLM 应用开发（最关键的一周）

| 日 | 任务 | 产出 |
|----|------|------|
| Day 8 | 1. 学习 LLM 基础概念（Transformer、Attention、Token）<br>2. 注册 OpenAI / Anthropic API Key<br>3. 用 Python 调用 ChatGPT API 完成 3 个 Prompt 实验 | API 调用脚本 |
| Day 9 | 1. 学习 LangChain 核心概念（Chain、Agent、Tool、Memory）<br>2. 搭建第一个 LangChain 对话机器人 | 代码提交 GitHub |
| Day 10 | 1. 学习 RAG 架构（文档加载 → 分块 → 嵌入 → 检索 → 生成）<br>2. 用 ChromaDB 构建本地向量数据库 | RAG 原型运行 |
| Day 11 | 1. 开发 **项目一：个人知识库问答系统**<br>2. 功能：上传 PDF → 自动分块 → 向量化 → 用自然语言提问 → 返回答案+来源 | 项目 V1 完成 |
| Day 12 | 1. 为项目一添加 Streamlit/Gradio 前端界面<br>2. 支持多文档上传、历史对话显示 | 可演示的 Web 界面 |
| Day 13 | 1. 部署项目一到 Hugging Face Spaces 或 Streamlit Cloud<br>2. 写完整 README（截图 + 架构图 + 使用说明） | **🔗 在线 Demo 链接** |
| Day 14 | 1. 在 LinkedIn 发布项目一介绍帖（附 Demo 链接和 GitHub）<br>2. 在 Twitter/X 发布英文版项目介绍 | 社交媒体曝光 |

#### 第 3 周（Day 15–21）：AI Agent + 第二个项目

| 日 | 任务 | 产出 |
|----|------|------|
| Day 15 | 1. 学习 AI Agent 概念（ReAct、Tool Use、Planning）<br>2. 用 LangGraph 搭建一个简单的 Agent 示例 | Agent 原型 |
| Day 16 | 1. 开发 **项目二：AI 自动化研究助理 Agent**<br>2. 功能：输入研究主题 → 自动搜索网页 → 汇总报告 → 生成 Markdown | 项目 V1 |
| Day 17 | 1. 为 Agent 添加更多工具（代码执行、文件读写、数据分析）<br>2. 实现多步推理和自我修正 | 增强版 Agent |
| Day 18 | 1. 添加前端 + 部署到 Hugging Face Spaces<br>2. 写完整 README | **🔗 在线 Demo 链接** |
| Day 19 | 1. 学习 Hugging Face Transformers 库<br>2. 用预训练模型做文本分类/情感分析实验 | 实验代码 |
| Day 20 | 1. 学习 LoRA 微调原理<br>2. 对一个小模型（如 Llama-3-8B 或 Mistral-7B）做简单微调 | 微调脚本 |
| Day 21 | 1. 发布微调模型到 Hugging Face Hub<br>2. 写模型卡片（Model Card）<br>3. 在 LinkedIn 分享项目二 | 模型发布 + 社交曝光 |

#### 第 4 周（Day 22–30）：求职冲刺

| 日 | 任务 | 产出 |
|----|------|------|
| Day 22 | 1. 更新简历（AI 项目经验突出）<br>2. 针对丹麦/加拿大格式优化（一页简历，无照片） | 英文简历 V1 |
| Day 23 | 1. 优化 LinkedIn 个人资料（AI/ML Engineer 标题）<br>2. 添加项目截图、Demo 链接、技能标签<br>3. 开启 #OpenToWork 标识 | LinkedIn 优化完成 |
| Day 24 | 1. 优化 GitHub Profile README（置顶 AI 项目）<br>2. 确保每个项目都有详细 README + Demo GIF | GitHub 作品集完善 |
| Day 25 | 1. 写 2 篇技术博客发布到 Medium / dev.to<br>  - 「How I Built a RAG System from Scratch」<br>  - 「Building an AI Agent with LangGraph」 | 2 篇博客发布 |
| Day 26 | 1. 研究目标公司列表（丹麦 10 家 + 加拿大 10 家）<br>2. 丹麦：Novo Nordisk、Maersk、Vestas、Lunar、Corti AI、Supwiz<br>3. 加拿大：Cohere、Ada、Shopify、Wealthsimple、Element AI（ServiceNow） | 目标公司清单 |
| Day 27 | 1. 为每家公司定制 Cover Letter 模板<br>2. 在 LinkedIn 上连接每家公司的 AI 团队成员（发 Connection 请求时附简短自我介绍） | Cover Letter 模板 |
| Day 28 | 1. 投递第一批简历（5 家丹麦 + 5 家加拿大）<br>2. 在 LinkedIn Jobs、Glassdoor、The Hub（丹麦）、Indeed Canada 上搜索并投递 | 10 份投递完成 |
| Day 29 | 1. 准备技术面试：LeetCode 中等难度 5 题（Python）<br>2. 准备 ML 系统设计题：推荐系统 / 搜索排序 / 实时 ML Pipeline | 面试准备笔记 |
| Day 30 | 1. 模拟面试（找朋友或用 [Pramp](https://www.pramp.com/) 平台）<br>2. 复盘 30 天成果：≥2 个部署项目 + ≥2 篇博客 + ≥10 份投递<br>3. 制定下一个 30 天计划（持续投递 + 准备面试 + 新项目） | 30 天总结 |

---

### 四、30 天成果检查清单

```
✅ 完成检查清单（Day 30 时对照）：

□ GitHub 上有 ≥3 个 AI 项目（含完整 README）
□ 至少 1 个项目有在线 Demo（Hugging Face Spaces / Streamlit Cloud）
□ 至少 1 个微调模型发布到 Hugging Face Hub
□ LinkedIn 已优化，标题包含 "AI/ML Engineer"
□ 已发布 ≥2 篇英文技术博客
□ 已投递 ≥10 份 AI 工程师岗位（丹麦 + 加拿大）
□ Kaggle 至少完成 1 个竞赛并发布 Notebook
□ 已获得 ≥3 个 Kaggle 微课程证书
```

---

### 五、丹麦/加拿大求职实用资源

#### 🇩🇰 丹麦

| 资源 | 链接 | 说明 |
|------|------|------|
| The Hub | [thehub.io](https://thehub.io/) | 北欧最大科技求职平台 |
| Jobindex | [jobindex.dk](https://www.jobindex.dk/) | 丹麦最大综合求职网站 |
| Work in Denmark | [workindenmark.dk](https://www.workindenmark.dk/) | 官方外国人求职指南 |
| Fast-track 签证 | [nyidanmark.dk](https://www.nyidanmark.dk/) | IT 快速通道工作许可 |
| Copenhagen AI Meetup | Meetup.com 搜索 | 线下 AI 社区活动 |

#### 🇨🇦 加拿大

| 资源 | 链接 | 说明 |
|------|------|------|
| Indeed Canada | [indeed.ca](https://www.indeed.ca/) | 最大综合求职平台 |
| LinkedIn Jobs | [linkedin.com/jobs](https://www.linkedin.com/jobs/) | AI 岗位最集中 |
| Global Talent Stream | [canada.ca/global-talent](https://www.canada.ca/en/employment-social-development/services/foreign-workers/global-talent.html) | 2 周快速工签 |
| Express Entry | [canada.ca/express-entry](https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html) | PR 永居路径 |
| Toronto Machine Learning Society | [torontoml.com](https://torontoml.com/) | 多伦多 AI 社区 |
| Mila (蒙特利尔) | [mila.quebec](https://mila.quebec/en/) | 世界顶级 AI 研究所（有产业合作岗位） |

---

## 推荐学习资源

### 视频课程
- [Cyfrin Updraft - Solidity Fundamentals](https://updraft.cyfrin.io/)（免费，Patrick Collins 出品）
- [Buildspace - Build your own DeFi dApp](https://buildspace.so/)
- [LearnWeb3 DAO](https://learnweb3.io/)（系统化路线，免费）

### 文档
- [Ethereum.org Developer Docs](https://ethereum.org/en/developers/docs/)
- [Solidity 官方文档](https://docs.soliditylang.org/)
- [OpenZeppelin Contracts 文档](https://docs.openzeppelin.com/contracts/)

### 实战平台
- [Ethernaut](https://ethernaut.openzeppelin.com/)（安全 CTF）
- [Damn Vulnerable DeFi](https://www.damnvulnerabledefi.xyz/)（DeFi 安全）
- [Speed Run Ethereum](https://speedrunethereum.com/)（实战挑战）

### 社区
- [ETHGlobal Discord](https://discord.gg/ethglobal)
- [Buildspace Discord](https://discord.gg/buildspace)
- [Telegram：Web3中文开发者群](https://t.me/ETH_CN)

---

## 完成情况统计

```
第一个月（Day 1–30）：  ⬜ 0 / 30 天完成
第二个月（Day 31–60）： ⬜ 0 / 30 天完成
总体进度：             ⬜ 0 / 60 天完成
```

> **提示**：每完成一天，将对应行的 `⬜` 改为 `✅`，并在 commit message 中注明（如 `Day 5: 完成以太坊交易练习`）。坚持打卡，Go Build！🚀