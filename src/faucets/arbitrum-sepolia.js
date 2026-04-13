const { rateLimitedRequest, checkCooldown, recordClaim } = require('./utils');
const logger = require('../logger');

const FAUCET_NAME = 'arbitrum-sepolia';
const COOLDOWN_HOURS = 24;

// Arbitrum Sepolia faucets
const FAUCET_URLS = [
  {
    name: 'Arbitrum Sepolia QuickNode',
    url: 'https://faucet.quicknode.com/drip',
    method: 'POST',
    buildPayload: (addr) => ({ chain: 'arbitrum-sepolia', wallet: addr }),
  },
];

module.exports = {
  name: 'Arbitrum Sepolia ETH Faucet',
  chain: 'arbitrumSepolia',
  cooldownHours: COOLDOWN_HOURS,

  async claim(walletAddress) {
    if (!checkCooldown(FAUCET_NAME, walletAddress, COOLDOWN_HOURS)) {
      logger.info(`[Arb Sepolia] Cooldown active for ${walletAddress.slice(0, 10)}...`);
      return { success: false, reason: 'cooldown' };
    }

    for (const faucet of FAUCET_URLS) {
      try {
        logger.info(`[Arb Sepolia] Trying ${faucet.name} for ${walletAddress.slice(0, 10)}...`);

        const response = await rateLimitedRequest(faucet.url, {
          method: faucet.method,
          headers: { 'Content-Type': 'application/json' },
          data: faucet.buildPayload(walletAddress),
        });

        if (response.status === 200) {
          const txHash = response.data?.txHash || response.data?.hash || null;
          logger.success(`[Arb Sepolia] Claimed from ${faucet.name}`);
          recordClaim(FAUCET_NAME, walletAddress, txHash);
          return { success: true, txHash };
        }
      } catch (error) {
        const msg = error.response ? `HTTP ${error.response.status}` : error.message;
        logger.warn(`[Arb Sepolia] ${faucet.name} failed: ${msg}`);
      }
    }

    logger.error(`[Arb Sepolia] All faucets failed for ${walletAddress.slice(0, 10)}...`);
    return { success: false, reason: 'all_faucets_failed' };
  },
};
