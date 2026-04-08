require('dotenv').config();

const config = {
  // Wallet
  walletPassword: process.env.WALLET_PASSWORD || '',
  walletCount: parseInt(process.env.WALLET_COUNT, 10) || 3,

  // Schedules
  faucetSchedule: process.env.FAUCET_SCHEDULE || '0 8 * * *',
  protocolSchedule: process.env.PROTOCOL_SCHEDULE || '0 */12 * * *',
  trackerSchedule: process.env.TRACKER_SCHEDULE || '0 */6 * * *',

  // Chains
  enableSepolia: process.env.ENABLE_SEPOLIA !== '0',
  enableBaseSepolia: process.env.ENABLE_BASE_SEPOLIA !== '0',
  enableArbitrumSepolia: process.env.ENABLE_ARBITRUM_SEPOLIA !== '0',

  // RPC endpoints
  rpc: {
    sepolia: process.env.SEPOLIA_RPC || 'https://rpc.sepolia.org',
    baseSepolia: process.env.BASE_SEPOLIA_RPC || 'https://sepolia.base.org',
    arbitrumSepolia: process.env.ARBITRUM_SEPOLIA_RPC || 'https://sepolia-rollup.arbitrum.io/rpc',
  },

  // Anti-detection
  minDelay: parseInt(process.env.MIN_DELAY, 10) || 60,
  maxDelay: parseInt(process.env.MAX_DELAY, 10) || 300,
  scheduleJitter: parseInt(process.env.SCHEDULE_JITTER, 10) || 30,

  // Paths
  dataDir: require('path').join(__dirname, '..', 'data'),
  walletsFile: require('path').join(__dirname, '..', 'data', 'wallets.enc'),
  activityLog: require('path').join(__dirname, '..', 'data', 'activity-log.json'),
};

/**
 * Validate that required config values are present.
 * Returns an array of error messages (empty if valid).
 */
function validate() {
  const errors = [];
  if (!config.walletPassword) {
    errors.push('WALLET_PASSWORD is required. Run "npm run setup" or set it in .env');
  }
  if (config.walletCount < 1 || config.walletCount > 10) {
    errors.push('WALLET_COUNT must be between 1 and 10');
  }
  return errors;
}

module.exports = { ...config, validate };
