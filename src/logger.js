const chalk = require('chalk');
const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, '..', 'data');

function ensureDataDir() {
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }
}

function timestamp() {
  return new Date().toISOString().replace('T', ' ').substring(0, 19);
}

function writeToFile(level, message) {
  ensureDataDir();
  const logFile = path.join(dataDir, 'bot.log');
  const line = `[${timestamp()}] [${level}] ${message}\n`;
  fs.appendFileSync(logFile, line);
}

const logger = {
  info(message) {
    console.log(chalk.cyan(`[${timestamp()}] ℹ ${message}`));
    writeToFile('INFO', message);
  },

  success(message) {
    console.log(chalk.green(`[${timestamp()}] ✓ ${message}`));
    writeToFile('SUCCESS', message);
  },

  warn(message) {
    console.log(chalk.yellow(`[${timestamp()}] ⚠ ${message}`));
    writeToFile('WARN', message);
  },

  error(message) {
    console.log(chalk.red(`[${timestamp()}] ✗ ${message}`));
    writeToFile('ERROR', message);
  },

  divider() {
    console.log(chalk.gray('─'.repeat(50)));
  },
};

module.exports = logger;
