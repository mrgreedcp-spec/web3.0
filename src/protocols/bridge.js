const { ethers } = require('ethers');
const logger = require('../logger');
const config = require('../config');
const { recordInteraction } = require('../faucets/utils');

// Base Sepolia Official Bridge (L1 -> L2)
const BASE_BRIDGE_ADDRESS = '0xfd0Bf71F60660E2f608ed56e1659C450eB113120';
const BASE_BRIDGE_ABI = [
  'function depositETH(uint32 _minGasLimit, bytes calldata _extraData) external payable',
];

// Arbitrum Sepolia Delayed Inbox
const ARB_INBOX_ADDRESS = '0xaAe29B0366299461418F5324a79Afc425BE5ae21';
const ARB_INBOX_ABI = [
  'function depositEth() external payable returns (uint256)',
];

module.exports = {
  name: 'Cross-chain Bridge',

  /**
   * Bridge a small amount of ETH from Sepolia to L2 testnets.
   * This creates valuable cross-chain activity for airdrop qualification.
   */
  async execute(wallet, chainName) {
    // Bridge only works from Sepolia L1
    if (chainName !== 'sepolia') {
      logger.info(`[Bridge] Bridging only from Sepolia L1, skipping ${chainName}`);
      return { success: false, reason: 'wrong_chain' };
    }

    const balance = await wallet.provider.getBalance(wallet.address);
    const minBalance = ethers.parseEther('0.002');

    if (balance < minBalance) {
      logger.warn(`[Bridge] Insufficient balance for bridging, need at least 0.002 ETH`);
      return { success: false, reason: 'insufficient_balance' };
    }

    // Small random bridge amount: 0.0001 - 0.0005 ETH
    const randomMultiplier = Math.floor(Math.random() * 5) + 1;
    const bridgeAmount = ethers.parseEther(`0.000${randomMultiplier}`);

    const results = [];

    // Bridge to Base Sepolia
    if (config.enableBaseSepolia) {
      try {
        logger.info(`[Bridge] Bridging ${ethers.formatEther(bridgeAmount)} ETH to Base Sepolia...`);
        const bridge = new ethers.Contract(BASE_BRIDGE_ADDRESS, BASE_BRIDGE_ABI, wallet);
        const tx = await bridge.depositETH(200000, '0x', { value: bridgeAmount });
        const receipt = await tx.wait();
        logger.success(`[Bridge] Bridged to Base Sepolia! TX: ${receipt.hash}`);
        recordInteraction('bridge-base', wallet.address, 'bridge to Base Sepolia', receipt.hash);
        results.push({ chain: 'base-sepolia', success: true, txHash: receipt.hash });
      } catch (error) {
        logger.error(`[Bridge] Base Sepolia bridge failed: ${error.message}`);
        results.push({ chain: 'base-sepolia', success: false, reason: error.message });
      }
    }

    // Bridge to Arbitrum Sepolia
    if (config.enableArbitrumSepolia) {
      try {
        logger.info(`[Bridge] Bridging ${ethers.formatEther(bridgeAmount)} ETH to Arbitrum Sepolia...`);
        const inbox = new ethers.Contract(ARB_INBOX_ADDRESS, ARB_INBOX_ABI, wallet);
        const tx = await inbox.depositEth({ value: bridgeAmount });
        const receipt = await tx.wait();
        logger.success(`[Bridge] Bridged to Arbitrum Sepolia! TX: ${receipt.hash}`);
        recordInteraction('bridge-arbitrum', wallet.address, 'bridge to Arbitrum Sepolia', receipt.hash);
        results.push({ chain: 'arbitrum-sepolia', success: true, txHash: receipt.hash });
      } catch (error) {
        logger.error(`[Bridge] Arbitrum Sepolia bridge failed: ${error.message}`);
        results.push({ chain: 'arbitrum-sepolia', success: false, reason: error.message });
      }
    }

    const anySuccess = results.some((r) => r.success);
    return { success: anySuccess, results };
  },
};
