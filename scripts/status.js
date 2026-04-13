require('dotenv').config();
const chalk = require('chalk');
const config = require('../src/config');
const walletManager = require('../src/wallet/manager');
const { loadActivityLog } = require('../src/faucets/utils');
const tracker = require('../src/tracker');

async function main() {
  console.log('');
  console.log(chalk.bold.cyan('  Web3 Airdrop Farmer - Status Dashboard'));
  console.log(chalk.gray('  ' + '─'.repeat(45)));

  // Validate config
  const errors = config.validate();
  if (errors.length > 0) {
    console.log(chalk.red('\n  Configuration errors:'));
    errors.forEach((e) => console.log(chalk.red(`    - ${e}`)));
    console.log(chalk.yellow(`\n  Run ${chalk.cyan('npm run setup')} to configure.`));
    process.exit(1);
  }

  // Load wallets
  const addresses = walletManager.listAddresses();
  if (!addresses || addresses.length === 0) {
    console.log(chalk.red('\n  No wallets found. Run "npm run setup" first.'));
    process.exit(1);
  }

  // Display wallets and balances
  console.log(chalk.bold('\n  Wallets:'));
  const chains = [];
  if (config.enableSepolia) chains.push({ name: 'Sepolia', key: 'sepolia' });
  if (config.enableBaseSepolia) chains.push({ name: 'Base Sepolia', key: 'baseSepolia' });
  if (config.enableArbitrumSepolia) chains.push({ name: 'Arb Sepolia', key: 'arbitrumSepolia' });

  for (let i = 0; i < addresses.length; i++) {
    console.log(chalk.cyan(`\n    Wallet ${i + 1}: ${addresses[i]}`));

    for (const chain of chains) {
      try {
        const balance = await walletManager.getBalance(i, chain.key);
        const balanceNum = parseFloat(balance);
        const color = balanceNum > 0 ? chalk.green : chalk.gray;
        console.log(`      ${chain.name}: ${color(balance + ' ETH')}`);
      } catch {
        console.log(`      ${chain.name}: ${chalk.gray('(unable to fetch)')}`);
      }
    }
  }

  // Activity summary
  const log = loadActivityLog();
  console.log(chalk.bold('\n  Activity Summary:'));
  console.log(`    Faucet claims: ${chalk.cyan(log.claims ? log.claims.length : 0)}`);
  console.log(`    Protocol interactions: ${chalk.cyan(log.interactions ? log.interactions.length : 0)}`);

  if (log.claims && log.claims.length > 0) {
    const lastClaim = log.claims[log.claims.length - 1];
    console.log(`    Last claim: ${chalk.gray(lastClaim.faucet)} at ${chalk.gray(lastClaim.timestamp)}`);
  }

  if (log.interactions && log.interactions.length > 0) {
    const lastInteraction = log.interactions[log.interactions.length - 1];
    console.log(`    Last interaction: ${chalk.gray(lastInteraction.protocol)} at ${chalk.gray(lastInteraction.timestamp)}`);
  }

  // Airdrop opportunities
  console.log(chalk.bold('\n  Airdrop Opportunities:'));
  const opportunities = tracker.loadCached();
  if (opportunities.length > 0) {
    tracker.display(opportunities);
  } else {
    console.log(chalk.gray('    No cached opportunities. They will be fetched when the bot runs.'));
  }

  // Funding tracker (information advantage)
  const fundingRounds = tracker.loadCachedFunding();
  if (fundingRounds.length > 0) {
    tracker.displayFunding(fundingRounds);
  } else {
    console.log(chalk.gray('\n    No funding data yet. It will be fetched when the bot runs.'));
  }

  // Schedules
  console.log(chalk.bold('\n  Schedules:'));
  console.log(`    Faucet claims:        ${chalk.cyan(config.faucetSchedule)}`);
  console.log(`    Protocol interactions: ${chalk.cyan(config.protocolSchedule)}`);
  console.log(`    Tracker refresh:      ${chalk.cyan(config.trackerSchedule)}`);
  console.log(`    Random jitter:        ${chalk.cyan('0-' + config.scheduleJitter + ' minutes')}`);

  console.log(chalk.gray('\n  ' + '─'.repeat(45)));
  console.log('');
}

main().catch((error) => {
  console.error(chalk.red('Status check failed:'), error.message);
  process.exit(1);
});
