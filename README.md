# Web3 Airdrop Farmer

Automated testnet faucet claiming and airdrop farming bot. Zero cost, fully automated, no human interaction required.

## DISCLAIMER

**Airdrop earnings are SPECULATIVE and NOT GUARANTEED.**

- Testnet activity may or may not qualify for future token airdrops
- Many projects explicitly disqualify bot-like behavior
- There is NO certainty of any financial return
- This tool automates repetitive testnet interactions that some people do manually
- Past examples (Arbitrum, Optimism) rewarded some testnet users, but most projects do not

**This bot operates ONLY on testnets. No real funds are at risk.**

## What It Does

1. **Faucet Auto-Claiming**: Automatically claims free testnet ETH from multiple faucets (Sepolia, Base Sepolia, Arbitrum Sepolia)
2. **Protocol Interactions**: Deploys contracts, swaps on Uniswap V3 testnet, bridges between chains, and performs other on-chain activities
3. **Airdrop Tracking**: Monitors known airdrop opportunities from public sources
4. **Scheduling**: Runs all tasks on configurable cron schedules with random jitter for anti-detection

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Run interactive setup wizard
npm run setup

# 3. Start the bot
npm start
```

## Commands

| Command | Description |
|---------|-------------|
| `npm run setup` | Interactive setup wizard - creates wallets and configuration |
| `npm start` | Start the bot (runs continuously with scheduled tasks) |
| `npm run status` | View wallet balances, activity summary, and airdrop opportunities |
| `npm run claim` | Manually trigger faucet claims |
| `npm run interact` | Manually trigger protocol interactions |

## How It Works

### Wallets
- Creates multiple wallets (configurable, default 3) to increase coverage
- Private keys are encrypted with AES-256-GCM and stored locally
- Only wallet addresses are ever displayed; private keys never appear in logs

### Faucet Claiming
- Claims testnet ETH from API-based and PoW faucets (no CAPTCHA)
- Respects cooldown periods to avoid rate limiting
- Retries with exponential backoff on failures

### Protocol Interactions
- **Contract Deployment**: Deploys a simple storage contract on each chain
- **Uniswap V3 Swaps**: Wraps ETH and swaps on Sepolia testnet
- **Cross-chain Bridging**: Bridges ETH from Sepolia to Base and Arbitrum L2 testnets
- **General Activity**: Self-transfers, micro-sends to build transaction history

### Anti-Detection
- Random delays between transactions (1-5 minutes)
- Shuffled interaction order for each run
- Varied transaction amounts
- Staggered wallet activity
- Random jitter on scheduled tasks (0-30 minutes)

## Configuration

After running `npm run setup`, your `.env` file will contain:

| Variable | Default | Description |
|----------|---------|-------------|
| `WALLET_PASSWORD` | (required) | Encryption password for wallet storage |
| `WALLET_COUNT` | 3 | Number of wallets to manage |
| `FAUCET_SCHEDULE` | `0 8 * * *` | When to claim faucets (cron) |
| `PROTOCOL_SCHEDULE` | `0 */12 * * *` | When to interact with protocols (cron) |
| `ENABLE_SEPOLIA` | 1 | Enable Sepolia chain |
| `ENABLE_BASE_SEPOLIA` | 1 | Enable Base Sepolia chain |
| `ENABLE_ARBITRUM_SEPOLIA` | 1 | Enable Arbitrum Sepolia chain |
| `MIN_DELAY` | 60 | Min seconds between transactions |
| `MAX_DELAY` | 300 | Max seconds between transactions |
| `SCHEDULE_JITTER` | 30 | Max random minutes added to schedules |

## Project Structure

```
web3.0/
├── index.js                     # Main entry point
├── package.json                 # Dependencies and scripts
├── .env.example                 # Configuration template
├── src/
│   ├── config.js                # Configuration loader
│   ├── logger.js                # Logging utility
│   ├── wallet/
│   │   ├── manager.js           # Wallet creation and management
│   │   └── store.js             # AES-256-GCM encrypted storage
│   ├── faucets/
│   │   ├── index.js             # Faucet coordinator
│   │   ├── sepolia.js           # Sepolia faucet
│   │   ├── base-sepolia.js      # Base Sepolia faucet
│   │   ├── arbitrum-sepolia.js  # Arbitrum Sepolia faucet
│   │   └── utils.js             # Shared utilities
│   ├── protocols/
│   │   ├── index.js             # Protocol coordinator
│   │   ├── deploy.js            # Contract deployment
│   │   ├── uniswap-testnet.js   # Uniswap V3 swaps
│   │   ├── bridge.js            # Cross-chain bridges
│   │   └── dapps.js             # General dApp interactions
│   ├── tracker/
│   │   ├── index.js             # Opportunity aggregator
│   │   └── sources.js           # Data sources
│   └── scheduler/
│       └── index.js             # Cron job manager
├── scripts/
│   ├── setup.js                 # Interactive setup wizard
│   └── status.js                # Status dashboard
└── data/                        # Runtime data (gitignored)
    ├── wallets.enc              # Encrypted wallets
    └── activity-log.json        # Activity history
```

## Security

- Private keys encrypted with AES-256-GCM (scrypt key derivation)
- `.env` and `data/` directory are gitignored
- **Testnet only** - no mainnet functionality exists in this codebase
- Minimal dependencies (7 total), all well-known packages

## Supported Chains

| Chain | Type | Faucet | Protocols |
|-------|------|--------|-----------|
| Sepolia | Ethereum L1 Testnet | PoW faucet | Uniswap, Bridge, Deploy |
| Base Sepolia | Base L2 Testnet | API faucet | Deploy, dApps |
| Arbitrum Sepolia | Arbitrum L2 Testnet | API faucet | Deploy, dApps |

## Troubleshooting

- **"No wallets found"**: Run `npm run setup` first
- **"WALLET_PASSWORD is required"**: Create a `.env` file or run `npm run setup`
- **Faucet claims failing**: Faucets frequently change; check logs in `data/bot.log`
- **Insufficient balance**: Wait for faucet claims to succeed before running interactions
- **RPC errors**: Free public RPCs have rate limits; try again later or set custom RPCs in `.env`
