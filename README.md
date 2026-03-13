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