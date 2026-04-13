const config = require('../config');
const walletManager = require('../wallet/manager');
const logger = require('../logger');
const { sleep, getRandomDelay } = require('./utils');

// Import faucet modules
const sepoliaFaucet = require('./sepolia');
const baseSepoliaFaucet = require('./base-sepolia');
const arbitrumSepoliaFaucet = require('./arbitrum-sepolia');

/**
 * Get list of enabled faucets based on config.
 */
function getEnabledFaucets() {
  const faucets = [];
  if (config.enableSepolia) faucets.push(sepoliaFaucet);
  if (config.enableBaseSepolia) faucets.push(baseSepoliaFaucet);
  if (config.enableArbitrumSepolia) faucets.push(arbitrumSepoliaFaucet);
  return faucets;
}

/**
 * Run all faucet claims for all wallets.
 */
async function runAll() {
  const wallets = walletManager.loadWallets();
  if (!wallets || wallets.length === 0) {
    logger.error('No wallets found. Run "npm run setup" first.');
    return;
  }

  const faucets = getEnabledFaucets();
  if (faucets.length === 0) {
    logger.warn('No faucets enabled. Check your .env configuration.');
    return;
  }

  logger.divider();
  logger.info(`Starting faucet claims for ${wallets.length} wallets across ${faucets.length} chains`);
  logger.divider();

  let totalSuccess = 0;
  let totalFailed = 0;

  for (const wallet of wallets) {
    for (const faucet of faucets) {
      try {
        const result = await faucet.claim(wallet.address);
        if (result.success) {
          totalSuccess++;
        } else {
          totalFailed++;
        }
      } catch (error) {
        logger.error(`Unexpected error claiming ${faucet.name}: ${error.message}`);
        totalFailed++;
      }

      // Random delay between claims to avoid detection
      const delay = getRandomDelay();
      logger.info(`Waiting ${Math.round(delay / 1000)}s before next claim...`);
      await sleep(delay);
    }
  }

  logger.divider();
  logger.info(`Faucet claims complete: ${totalSuccess} success, ${totalFailed} failed`);
  logger.divider();
}

module.exports = { runAll, getEnabledFaucets };
