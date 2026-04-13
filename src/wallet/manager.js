const { ethers } = require('ethers');
const config = require('../config');
const store = require('./store');
const logger = require('../logger');

let cachedWallets = null;

/**
 * Create new random wallets.
 */
function createWallets(count) {
  const wallets = [];
  for (let i = 0; i < count; i++) {
    wallets.push(ethers.Wallet.createRandom());
  }
  return wallets;
}

/**
 * Save wallets to encrypted storage.
 */
function saveWallets(wallets) {
  const privateKeys = wallets.map((w) => w.privateKey);
  store.saveWallets(config.walletsFile, privateKeys, config.walletPassword);
  logger.success(`Saved ${wallets.length} wallets to encrypted storage`);
}

/**
 * Load wallets from encrypted storage.
 * Returns array of ethers.Wallet instances (not connected to any provider).
 */
function loadWallets() {
  if (cachedWallets) return cachedWallets;

  const privateKeys = store.loadWallets(config.walletsFile, config.walletPassword);
  if (!privateKeys) {
    return null;
  }

  cachedWallets = privateKeys.map((pk) => new ethers.Wallet(pk));
  return cachedWallets;
}

/**
 * Load or create wallets. Creates new wallets if none exist.
 */
function loadOrCreate() {
  if (store.walletsExist(config.walletsFile)) {
    const wallets = loadWallets();
    logger.info(`Loaded ${wallets.length} existing wallets`);
    return wallets;
  }

  logger.info(`Creating ${config.walletCount} new wallets...`);
  const wallets = createWallets(config.walletCount);
  saveWallets(wallets);
  cachedWallets = wallets;
  return wallets;
}

/**
 * Get a wallet connected to a specific chain's provider.
 */
function getConnectedWallet(walletIndex, chainName) {
  const wallets = loadWallets();
  if (!wallets || walletIndex >= wallets.length) {
    throw new Error(`Wallet index ${walletIndex} not found`);
  }

  const rpcUrl = config.rpc[chainName];
  if (!rpcUrl) {
    throw new Error(`Unknown chain: ${chainName}`);
  }

  const provider = new ethers.JsonRpcProvider(rpcUrl);
  return wallets[walletIndex].connect(provider);
}

/**
 * Get all wallet addresses (safe to display).
 */
function listAddresses() {
  const wallets = loadWallets();
  if (!wallets) return [];
  return wallets.map((w) => w.address);
}

/**
 * Get balance of a wallet on a specific chain.
 */
async function getBalance(walletIndex, chainName) {
  const wallet = getConnectedWallet(walletIndex, chainName);
  const balance = await wallet.provider.getBalance(wallet.address);
  return ethers.formatEther(balance);
}

module.exports = {
  createWallets,
  saveWallets,
  loadWallets,
  loadOrCreate,
  getConnectedWallet,
  listAddresses,
  getBalance,
};
