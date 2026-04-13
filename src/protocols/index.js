const config = require('../config');
const walletManager = require('../wallet/manager');
const logger = require('../logger');
const { sleep, getRandomDelay, shuffle } = require('../faucets/utils');

// Import protocol modules
const deployProtocol = require('./deploy');
const uniswapProtocol = require('./uniswap-testnet');
const bridgeProtocol = require('./bridge');
const dappsProtocol = require('./dapps');

const ALL_PROTOCOLS = [deployProtocol, uniswapProtocol, bridgeProtocol, dappsProtocol];

/**
 * Get enabled chains as an array of { name, enabled } objects.
 */
function getEnabledChains() {
  const chains = [];
  if (config.enableSepolia) chains.push('sepolia');
  if (config.enableBaseSepolia) chains.push('baseSepolia');
  if (config.enableArbitrumSepolia) chains.push('arbitrumSepolia');
  return chains;
}

/**
 * Run all protocol interactions for all wallets across all enabled chains.
 */
async function runAll() {
  const wallets = walletManager.loadWallets();
  if (!wallets || wallets.length === 0) {
    logger.error('No wallets found. Run "npm run setup" first.');
    return;
  }

  const chains = getEnabledChains();
  if (chains.length === 0) {
    logger.warn('No chains enabled. Check your .env configuration.');
    return;
  }

  logger.divider();
  logger.info(`Starting protocol interactions for ${wallets.length} wallets on ${chains.length} chains`);
  logger.divider();

  let totalSuccess = 0;
  let totalFailed = 0;

  for (let i = 0; i < wallets.length; i++) {
    for (const chainName of chains) {
      // Get wallet connected to this chain
      const connectedWallet = walletManager.getConnectedWallet(i, chainName);

      // Shuffle protocols for each wallet/chain combo to avoid patterns
      const protocols = shuffle(ALL_PROTOCOLS);

      for (const protocol of protocols) {
        try {
          logger.info(`[${protocol.name}] Running on ${chainName}...`);
          const result = await protocol.execute(connectedWallet, chainName);

          if (result.success) {
            totalSuccess++;
          } else {
            totalFailed++;
          }
        } catch (error) {
          logger.error(`[${protocol.name}] Unexpected error: ${error.message}`);
          totalFailed++;
        }

        // Random delay between interactions
        const delay = getRandomDelay();
        logger.info(`Waiting ${Math.round(delay / 1000)}s before next interaction...`);
        await sleep(delay);
      }
    }

    // Extra delay between wallets to stagger activity
    if (i < wallets.length - 1) {
      const walletDelay = getRandomDelay() * 2;
      logger.info(`Waiting ${Math.round(walletDelay / 1000)}s before next wallet...`);
      await sleep(walletDelay);
    }
  }

  logger.divider();
  logger.info(`Protocol interactions complete: ${totalSuccess} success, ${totalFailed} failed`);
  logger.divider();
}

module.exports = { runAll, getEnabledChains };
