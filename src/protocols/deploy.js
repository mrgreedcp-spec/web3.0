const { ethers } = require('ethers');
const logger = require('../logger');
const { recordInteraction } = require('../faucets/utils');

// SimpleStorage contract - minimal contract for deployment
// Solidity: contract SimpleStorage { uint256 public value; function set(uint256 v) public { value = v; } }
const SIMPLE_STORAGE_ABI = [
  'function set(uint256 _value) public',
  'function value() public view returns (uint256)',
];
const SIMPLE_STORAGE_BYTECODE =
  '0x608060405234801561001057600080fd5b5060f78061001f6000396000f3fe6080604052348015600f57600080fd5b5060043610603c5760003560e01c80633fa4f24514604157806360fe47b114605b575b600080fd5b60476071565b604051605291906097565b60405180910390f35b606f60048036038101906069919060d8565b6077565b005b60005481565b8060008190555050565b6000819050919050565b609181608b565b82525050565b600060208201905060aa6000830184608a565b92915050565b600080fd5b60bf81608b565b811460c957600080fd5b50565b60008135905060d28160b8565b92915050565b60006020828403121560eb5760ea60b0565b5b600060f78482850160cc565b9150509291505056fea264697066735822';

module.exports = {
  name: 'Simple Contract Deploy',

  /**
   * Deploy a SimpleStorage contract and interact with it.
   * @param {ethers.Wallet} wallet - Connected wallet instance
   * @param {string} chainName - Chain identifier for logging
   */
  async execute(wallet, chainName) {
    try {
      logger.info(`[Deploy] Deploying SimpleStorage on ${chainName} from ${wallet.address.slice(0, 10)}...`);

      // Check balance first
      const balance = await wallet.provider.getBalance(wallet.address);
      if (balance === 0n) {
        logger.warn(`[Deploy] No balance on ${chainName} for ${wallet.address.slice(0, 10)}..., skipping`);
        return { success: false, reason: 'no_balance' };
      }

      // Deploy contract
      const factory = new ethers.ContractFactory(SIMPLE_STORAGE_ABI, SIMPLE_STORAGE_BYTECODE, wallet);
      const contract = await factory.deploy();
      await contract.waitForDeployment();

      const contractAddress = await contract.getAddress();
      logger.success(`[Deploy] Contract deployed at ${contractAddress} on ${chainName}`);
      recordInteraction('deploy', wallet.address, `deployed on ${chainName}`, contractAddress);

      // Interact: set a random value
      const randomValue = Math.floor(Math.random() * 10000);
      const tx = await contract.set(randomValue);
      await tx.wait();
      logger.success(`[Deploy] Set value to ${randomValue} on ${chainName}`);
      recordInteraction('deploy', wallet.address, `set value on ${chainName}`, tx.hash);

      return { success: true, contractAddress, txHash: tx.hash };
    } catch (error) {
      logger.error(`[Deploy] Failed on ${chainName}: ${error.message}`);
      return { success: false, reason: error.message };
    }
  },
};
