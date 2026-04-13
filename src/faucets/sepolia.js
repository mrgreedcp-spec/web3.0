const { rateLimitedRequest, checkCooldown, recordClaim } = require('./utils');
const logger = require('../logger');

const FAUCET_NAME = 'sepolia-pk910';
const COOLDOWN_HOURS = 24;

// pk910 PoW faucet - no CAPTCHA required, uses proof-of-work
const FAUCET_API = 'https://sepolia-faucet.pk910.de';

module.exports = {
  name: 'Sepolia ETH (pk910 PoW Faucet)',
  chain: 'sepolia',
  cooldownHours: COOLDOWN_HOURS,

  async claim(walletAddress) {
    if (!checkCooldown(FAUCET_NAME, walletAddress, COOLDOWN_HOURS)) {
      logger.info(`[Sepolia] Cooldown active for ${walletAddress.slice(0, 10)}...`);
      return { success: false, reason: 'cooldown' };
    }

    try {
      logger.info(`[Sepolia] Requesting faucet for ${walletAddress.slice(0, 10)}...`);

      // Try pk910 PoW faucet API - start a mining session
      const response = await rateLimitedRequest(
        `${FAUCET_API}/api/getToken`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          data: { addr: walletAddress },
        }
      );

      if (response.data && response.data.session) {
        logger.success(`[Sepolia] Faucet session started for ${walletAddress.slice(0, 10)}...`);
        recordClaim(FAUCET_NAME, walletAddress, response.data.session);
        return { success: true, session: response.data.session };
      }

      logger.warn(`[Sepolia] Unexpected response from faucet`);
      return { success: false, reason: 'unexpected_response' };
    } catch (error) {
      const msg = error.response ? `HTTP ${error.response.status}` : error.message;
      logger.error(`[Sepolia] Faucet claim failed: ${msg}`);
      return { success: false, reason: msg };
    }
  },
};
