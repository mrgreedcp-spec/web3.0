require('dotenv').config();
const config = require('./src/config');
const walletManager = require('./src/wallet/manager');
const scheduler = require('./src/scheduler');
const faucets = require('./src/faucets');
const tracker = require('./src/tracker');
const logger = require('./src/logger');

async function main() {
  console.log('');
  logger.divider();
  logger.info('Web3 Airdrop Farmer v1.0.0');
  logger.divider();
  console.log('');

  // Disclaimer
  logger.warn('DISCLAIMER: Airdrop earnings are speculative and NOT guaranteed.');
  logger.warn('This bot operates ONLY on testnets. No real funds are at risk.');
  console.log('');

  // Validate configuration
  const errors = config.validate();
  if (errors.length > 0) {
    errors.forEach((e) => logger.error(e));
    logger.error('Fix configuration issues and try again. Run "npm run setup" for guided setup.');
    process.exit(1);
  }

  // Load or create wallets
  const wallets = walletManager.loadOrCreate();
  logger.info(`Managing ${wallets.length} wallets`);

  // Display wallet addresses (never private keys)
  walletManager.listAddresses().forEach((addr, i) => {
    logger.info(`  Wallet ${i + 1}: ${addr}`);
  });
  console.log('');

  // Run initial faucet claim
  logger.info('Running initial faucet claims...');
  await faucets.runAll();

  // Refresh airdrop tracker
  logger.info('Refreshing airdrop opportunities...');
  await tracker.refresh();

  // Start scheduler for recurring tasks
  scheduler.start();

  console.log('');
  logger.success('Bot is running! Press Ctrl+C to stop.');
  logger.info('The bot will automatically claim faucets and interact with protocols on schedule.');
  logger.info('Run "npm run status" in another terminal to check progress.');
  console.log('');
}

main().catch((error) => {
  logger.error(`Fatal error: ${error.message}`);
  process.exit(1);
});
