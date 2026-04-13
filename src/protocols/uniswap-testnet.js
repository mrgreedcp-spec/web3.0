const { ethers } = require('ethers');
const logger = require('../logger');
const { recordInteraction } = require('../faucets/utils');

// Uniswap V3 SwapRouter on Sepolia
const SWAP_ROUTER_ADDRESS = '0x3bFA4769FB09eefC5a80d6E87c3B9C650f7Ae48E';
const WETH_SEPOLIA = '0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14';
const USDC_SEPOLIA = '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238';

// Minimal Uniswap SwapRouter ABI
const SWAP_ROUTER_ABI = [
  'function exactInputSingle((address tokenIn, address tokenOut, uint24 fee, address recipient, uint256 amountIn, uint256 amountOutMinimum, uint160 sqrtPriceLimitX96)) external payable returns (uint256 amountOut)',
];

// WETH ABI for wrapping
const WETH_ABI = [
  'function deposit() external payable',
  'function approve(address spender, uint256 amount) external returns (bool)',
  'function balanceOf(address owner) external view returns (uint256)',
];

module.exports = {
  name: 'Uniswap V3 Testnet Swap',

  /**
   * Perform a small swap on Uniswap V3 Sepolia testnet.
   * Wraps a tiny amount of ETH to WETH, then swaps WETH -> USDC.
   */
  async execute(wallet, chainName) {
    if (chainName !== 'sepolia') {
      logger.info(`[Uniswap] Only available on Sepolia, skipping ${chainName}`);
      return { success: false, reason: 'wrong_chain' };
    }

    try {
      logger.info(`[Uniswap] Starting swap on Sepolia for ${wallet.address.slice(0, 10)}...`);

      const balance = await wallet.provider.getBalance(wallet.address);
      const minBalance = ethers.parseEther('0.001');

      if (balance < minBalance) {
        logger.warn(`[Uniswap] Insufficient balance for swap, need at least 0.001 ETH`);
        return { success: false, reason: 'insufficient_balance' };
      }

      // Small random amount between 0.0001 and 0.0005 ETH
      const randomMultiplier = Math.floor(Math.random() * 5) + 1;
      const swapAmount = ethers.parseEther(`0.000${randomMultiplier}`);

      // Step 1: Wrap ETH to WETH
      const weth = new ethers.Contract(WETH_SEPOLIA, WETH_ABI, wallet);
      const wrapTx = await weth.deposit({ value: swapAmount });
      await wrapTx.wait();
      logger.success(`[Uniswap] Wrapped ${ethers.formatEther(swapAmount)} ETH to WETH`);

      // Step 2: Approve SwapRouter to spend WETH
      const approveTx = await weth.approve(SWAP_ROUTER_ADDRESS, swapAmount);
      await approveTx.wait();
      logger.success(`[Uniswap] Approved SwapRouter`);

      // Step 3: Swap WETH -> USDC
      const router = new ethers.Contract(SWAP_ROUTER_ADDRESS, SWAP_ROUTER_ABI, wallet);
      const swapParams = {
        tokenIn: WETH_SEPOLIA,
        tokenOut: USDC_SEPOLIA,
        fee: 3000, // 0.3% fee tier
        recipient: wallet.address,
        amountIn: swapAmount,
        amountOutMinimum: 0, // Testnet - no slippage concern
        sqrtPriceLimitX96: 0,
      };

      const swapTx = await router.exactInputSingle(swapParams);
      const receipt = await swapTx.wait();
      logger.success(`[Uniswap] Swap complete! TX: ${receipt.hash}`);
      recordInteraction('uniswap-v3', wallet.address, 'swap WETH->USDC on sepolia', receipt.hash);

      return { success: true, txHash: receipt.hash };
    } catch (error) {
      logger.error(`[Uniswap] Swap failed: ${error.message}`);
      return { success: false, reason: error.message };
    }
  },
};
