const { ethers } = require('ethers');
const logger = require('../logger');
const { recordInteraction } = require('../faucets/utils');

// Simple NFT minting - minimal ERC721 interaction
// Many testnet projects offer free mints
const MINT_FUNCTION_ABI = ['function mint() external'];

// Self-transfer: a simple way to create on-chain activity
module.exports = {
  name: 'Testnet dApp Interactions',

  /**
   * Perform miscellaneous testnet interactions to build on-chain history.
   */
  async execute(wallet, chainName) {
    const results = [];

    // 1. Self-transfer (creates transaction history on any chain)
    try {
      const balance = await wallet.provider.getBalance(wallet.address);
      const minBalance = ethers.parseEther('0.0005');

      if (balance >= minBalance) {
        // Random tiny amount
        const amount = ethers.parseEther('0.0001');
        logger.info(`[dApps] Self-transfer on ${chainName} for ${wallet.address.slice(0, 10)}...`);

        const tx = await wallet.sendTransaction({
          to: wallet.address,
          value: amount,
        });
        const receipt = await tx.wait();
        logger.success(`[dApps] Self-transfer complete on ${chainName}. TX: ${receipt.hash}`);
        recordInteraction('self-transfer', wallet.address, `self-transfer on ${chainName}`, receipt.hash);
        results.push({ action: 'self-transfer', success: true, txHash: receipt.hash });
      } else {
        logger.warn(`[dApps] Insufficient balance for self-transfer on ${chainName}`);
        results.push({ action: 'self-transfer', success: false, reason: 'no_balance' });
      }
    } catch (error) {
      logger.error(`[dApps] Self-transfer failed on ${chainName}: ${error.message}`);
      results.push({ action: 'self-transfer', success: false, reason: error.message });
    }

    // 2. Multi-send: split a tiny amount to create multiple transactions
    try {
      const balance = await wallet.provider.getBalance(wallet.address);
      const minBalance = ethers.parseEther('0.001');

      if (balance >= minBalance) {
        // Create a second random wallet and send a tiny amount
        const randomWallet = ethers.Wallet.createRandom();
        const amount = ethers.parseEther('0.00001');
        logger.info(`[dApps] Micro-send on ${chainName} to random address...`);

        const tx = await wallet.sendTransaction({
          to: randomWallet.address,
          value: amount,
        });
        const receipt = await tx.wait();
        logger.success(`[dApps] Micro-send complete on ${chainName}. TX: ${receipt.hash}`);
        recordInteraction('micro-send', wallet.address, `micro-send on ${chainName}`, receipt.hash);
        results.push({ action: 'micro-send', success: true, txHash: receipt.hash });
      }
    } catch (error) {
      logger.error(`[dApps] Micro-send failed on ${chainName}: ${error.message}`);
      results.push({ action: 'micro-send', success: false, reason: error.message });
    }

    const anySuccess = results.some((r) => r.success);
    return { success: anySuccess, results };
  },
};
