const axios = require('axios');
const fs = require('fs');
const config = require('../config');
const logger = require('../logger');

/**
 * Make an HTTP request with built-in delay for rate limiting.
 */
async function rateLimitedRequest(url, options = {}, delayMs = 2000) {
  await sleep(delayMs);
  try {
    const response = await axios({
      url,
      timeout: 30000,
      ...options,
    });
    return response;
  } catch (error) {
    if (error.response && error.response.status === 429) {
      logger.warn(`Rate limited by ${url}, waiting 60s...`);
      await sleep(60000);
      return axios({ url, timeout: 30000, ...options });
    }
    throw error;
  }
}

/**
 * Load activity log from disk.
 */
function loadActivityLog() {
  try {
    if (fs.existsSync(config.activityLog)) {
      return JSON.parse(fs.readFileSync(config.activityLog, 'utf8'));
    }
  } catch {
    // Corrupted log, start fresh
  }
  return { claims: [], interactions: [] };
}

/**
 * Save activity log to disk.
 */
function saveActivityLog(log) {
  const dir = require('path').dirname(config.activityLog);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(config.activityLog, JSON.stringify(log, null, 2));
}

/**
 * Check if enough time has passed since last claim for a faucet/wallet combo.
 */
function checkCooldown(faucetName, walletAddress, cooldownHours) {
  const log = loadActivityLog();
  const lastClaim = log.claims.find(
    (c) => c.faucet === faucetName && c.wallet === walletAddress
  );
  if (!lastClaim) return true;

  const elapsed = Date.now() - new Date(lastClaim.timestamp).getTime();
  const cooldownMs = cooldownHours * 60 * 60 * 1000;
  return elapsed >= cooldownMs;
}

/**
 * Record a successful faucet claim.
 */
function recordClaim(faucetName, walletAddress, txHash = null) {
  const log = loadActivityLog();
  // Remove old entry for this faucet/wallet combo
  log.claims = log.claims.filter(
    (c) => !(c.faucet === faucetName && c.wallet === walletAddress)
  );
  log.claims.push({
    faucet: faucetName,
    wallet: walletAddress,
    txHash,
    timestamp: new Date().toISOString(),
  });
  saveActivityLog(log);
}

/**
 * Record a protocol interaction.
 */
function recordInteraction(protocol, walletAddress, action, txHash = null) {
  const log = loadActivityLog();
  log.interactions.push({
    protocol,
    wallet: walletAddress,
    action,
    txHash,
    timestamp: new Date().toISOString(),
  });
  saveActivityLog(log);
}

/**
 * Sleep for specified milliseconds.
 */
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Get a random delay between min and max seconds (from config).
 */
function getRandomDelay() {
  const min = config.minDelay * 1000;
  const max = config.maxDelay * 1000;
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Shuffle an array (Fisher-Yates).
 */
function shuffle(array) {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

module.exports = {
  rateLimitedRequest,
  loadActivityLog,
  saveActivityLog,
  checkCooldown,
  recordClaim,
  recordInteraction,
  sleep,
  getRandomDelay,
  shuffle,
};
