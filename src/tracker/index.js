const fs = require('fs');
const path = require('path');
const config = require('../config');
const logger = require('../logger');
const { fetchOpportunities } = require('./sources');

const OPPORTUNITIES_FILE = path.join(config.dataDir, 'opportunities.json');

/**
 * Refresh airdrop opportunities and save to disk.
 */
async function refresh() {
  logger.info('[Tracker] Refreshing airdrop opportunities...');

  try {
    const opportunities = await fetchOpportunities();

    // Ensure data directory exists
    if (!fs.existsSync(config.dataDir)) {
      fs.mkdirSync(config.dataDir, { recursive: true });
    }

    fs.writeFileSync(OPPORTUNITIES_FILE, JSON.stringify({
      lastUpdated: new Date().toISOString(),
      count: opportunities.length,
      opportunities,
    }, null, 2));

    logger.success(`[Tracker] Found ${opportunities.length} opportunities`);
    return opportunities;
  } catch (error) {
    logger.error(`[Tracker] Refresh failed: ${error.message}`);
    return loadCached();
  }
}

/**
 * Load cached opportunities from disk.
 */
function loadCached() {
  try {
    if (fs.existsSync(OPPORTUNITIES_FILE)) {
      const data = JSON.parse(fs.readFileSync(OPPORTUNITIES_FILE, 'utf8'));
      return data.opportunities || [];
    }
  } catch {
    // Corrupted file
  }
  return [];
}

/**
 * Display opportunities in a formatted table.
 */
function display(opportunities) {
  const chalk = require('chalk');

  if (!opportunities || opportunities.length === 0) {
    logger.info('[Tracker] No opportunities found.');
    return;
  }

  console.log('');
  console.log(chalk.bold('  Airdrop Opportunities'));
  logger.divider();

  for (const opp of opportunities) {
    const statusColor = opp.status === 'active' ? chalk.green : chalk.yellow;
    console.log(
      `  ${chalk.bold(opp.project)} ${statusColor(`[${opp.status}]`)} - ${chalk.gray(opp.chain)}`
    );
    console.log(`    ${opp.description}`);
    if (opp.requirements && opp.requirements.length > 0) {
      opp.requirements.forEach((req) => {
        console.log(`    ${chalk.gray('- ' + req)}`);
      });
    }
    console.log('');
  }

  logger.divider();
}

module.exports = { refresh, loadCached, display };
