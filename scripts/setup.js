const inquirer = require('inquirer');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

const ROOT_DIR = path.join(__dirname, '..');
const ENV_FILE = path.join(ROOT_DIR, '.env');
const DATA_DIR = path.join(ROOT_DIR, 'data');

async function main() {
  console.log('');
  console.log(chalk.bold.cyan('  Web3 Airdrop Farmer - Setup Wizard'));
  console.log(chalk.gray('  ' + '─'.repeat(40)));
  console.log('');

  // Disclaimer
  console.log(chalk.yellow.bold('  IMPORTANT DISCLAIMER:'));
  console.log(chalk.yellow('  Airdrop earnings are SPECULATIVE and NOT GUARANTEED.'));
  console.log(chalk.yellow('  Testnet activity may or may not qualify for future airdrops.'));
  console.log(chalk.yellow('  This tool automates repetitive testnet interactions.'));
  console.log(chalk.yellow('  There is NO certainty of any financial return.'));
  console.log('');

  const { acknowledged } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'acknowledged',
      message: 'I understand the risks and want to proceed',
      default: false,
    },
  ]);

  if (!acknowledged) {
    console.log(chalk.red('Setup cancelled.'));
    process.exit(0);
  }

  // Wallet password
  const { password, passwordConfirm } = await inquirer.prompt([
    {
      type: 'password',
      name: 'password',
      message: 'Set a wallet encryption password (min 8 chars):',
      mask: '*',
      validate: (input) => {
        if (input.length < 8) return 'Password must be at least 8 characters';
        return true;
      },
    },
    {
      type: 'password',
      name: 'passwordConfirm',
      message: 'Confirm password:',
      mask: '*',
    },
  ]);

  if (password !== passwordConfirm) {
    console.log(chalk.red('Passwords do not match. Please try again.'));
    process.exit(1);
  }

  if (password.length < 12) {
    console.log(chalk.yellow('  Tip: A password of 12+ characters is recommended for stronger security.'));
  }

  // Wallet count
  const { walletCount } = await inquirer.prompt([
    {
      type: 'number',
      name: 'walletCount',
      message: 'How many wallets to create? (1-5):',
      default: 3,
      validate: (input) => {
        const n = parseInt(input, 10);
        if (n < 1 || n > 5) return 'Must be between 1 and 5';
        return true;
      },
    },
  ]);

  // Chain selection
  const { chains } = await inquirer.prompt([
    {
      type: 'checkbox',
      name: 'chains',
      message: 'Which chains to enable?',
      choices: [
        { name: 'Sepolia (Ethereum L1 testnet)', value: 'sepolia', checked: true },
        { name: 'Base Sepolia (Base L2 testnet)', value: 'baseSepolia', checked: true },
        { name: 'Arbitrum Sepolia (Arbitrum L2 testnet)', value: 'arbitrumSepolia', checked: true },
      ],
    },
  ]);

  if (chains.length === 0) {
    console.log(chalk.red('At least one chain must be enabled.'));
    process.exit(1);
  }

  // Write .env file
  const envContent = [
    '# Web3 Airdrop Farmer Configuration',
    `# Generated on ${new Date().toISOString()}`,
    '',
    `WALLET_PASSWORD=${password}`,
    `WALLET_COUNT=${walletCount}`,
    '',
    '# Schedules',
    'FAUCET_SCHEDULE=0 8 * * *',
    'PROTOCOL_SCHEDULE=0 */12 * * *',
    'TRACKER_SCHEDULE=0 */6 * * *',
    '',
    '# Chains',
    `ENABLE_SEPOLIA=${chains.includes('sepolia') ? '1' : '0'}`,
    `ENABLE_BASE_SEPOLIA=${chains.includes('baseSepolia') ? '1' : '0'}`,
    `ENABLE_ARBITRUM_SEPOLIA=${chains.includes('arbitrumSepolia') ? '1' : '0'}`,
    '',
    '# Anti-detection',
    'MIN_DELAY=60',
    'MAX_DELAY=300',
    'SCHEDULE_JITTER=30',
    '',
  ].join('\n');

  fs.writeFileSync(ENV_FILE, envContent);
  console.log(chalk.green('  ✓ Configuration saved to .env'));

  // Create data directory
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
  console.log(chalk.green('  ✓ Data directory created'));

  // Generate wallets
  // Need to load config after writing .env
  require('dotenv').config({ path: ENV_FILE });
  const { ethers } = require('ethers');
  const store = require('../src/wallet/store');
  const walletsFile = path.join(DATA_DIR, 'wallets.enc');

  const wallets = [];
  for (let i = 0; i < walletCount; i++) {
    wallets.push(ethers.Wallet.createRandom());
  }

  const privateKeys = wallets.map((w) => w.privateKey);
  store.saveWallets(walletsFile, privateKeys, password);
  console.log(chalk.green(`  ✓ Created and encrypted ${walletCount} wallets`));

  // Display wallet addresses
  console.log('');
  console.log(chalk.bold('  Your wallet addresses:'));
  wallets.forEach((w, i) => {
    console.log(chalk.cyan(`    Wallet ${i + 1}: ${w.address}`));
  });

  console.log('');
  console.log(chalk.gray('  ' + '─'.repeat(40)));
  console.log(chalk.bold.green('  Setup complete!'));
  console.log('');
  console.log(`  Run ${chalk.cyan('npm start')} to start the bot`);
  console.log(`  Run ${chalk.cyan('npm run status')} to check wallet status`);
  console.log(`  Run ${chalk.cyan('npm run claim')} to manually trigger faucet claims`);
  console.log('');
}

main().catch((error) => {
  console.error(chalk.red('Setup failed:'), error.message);
  process.exit(1);
});
