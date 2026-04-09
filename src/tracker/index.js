const fs = require('fs');
const path = require('path');
const config = require('../config');
const logger = require('../logger');
const { fetchOpportunities } = require('./sources');
const { fetchFundingRounds } = require('./funding');

const OPPORTUNITIES_FILE = path.join(config.dataDir, 'opportunities.json');
const FUNDING_FILE = path.join(config.dataDir, 'funding.json');

/**
 * Refresh airdrop opportunities and funding data, save to disk.
 */
async function refresh() {
  logger.info('[Tracker] Refreshing airdrop opportunities...');

  // Ensure data directory exists
  if (!fs.existsSync(config.dataDir)) {
    fs.mkdirSync(config.dataDir, { recursive: true });
  }

  // Fetch both in parallel
  const [opportunities, fundingRounds] = await Promise.all([
    fetchOpportunities().catch((err) => {
      logger.error(`[Tracker] Opportunities fetch failed: ${err.message}`);
      return loadCached();
    }),
    fetchFundingRounds().catch((err) => {
      logger.error(`[Tracker] Funding fetch failed: ${err.message}`);
      return loadCachedFunding();
    }),
  ]);

  // Save opportunities
  fs.writeFileSync(OPPORTUNITIES_FILE, JSON.stringify({
    lastUpdated: new Date().toISOString(),
    count: opportunities.length,
    opportunities,
  }, null, 2));

  // Save funding data
  fs.writeFileSync(FUNDING_FILE, JSON.stringify({
    lastUpdated: new Date().toISOString(),
    count: fundingRounds.length,
    rounds: fundingRounds,
  }, null, 2));

  const highPotential = fundingRounds.filter((r) => r.airdropPotential.level === 'HIGH');
  logger.success(`[Tracker] Found ${opportunities.length} opportunities, ${fundingRounds.length} funding rounds (${highPotential.length} HIGH potential)`);

  return { opportunities, fundingRounds };
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
 * Load cached funding data from disk.
 */
function loadCachedFunding() {
  try {
    if (fs.existsSync(FUNDING_FILE)) {
      const data = JSON.parse(fs.readFileSync(FUNDING_FILE, 'utf8'));
      return data.rounds || [];
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

/**
 * Display funding rounds with airdrop potential scores.
 */
function displayFunding(rounds) {
  const chalk = require('chalk');

  if (!rounds || rounds.length === 0) {
    logger.info('[Funding] No funding data found.');
    return;
  }

  console.log('');
  console.log(chalk.bold('  Funding Tracker - Potential Airdrop Candidates'));
  console.log(chalk.gray('  Projects that raised money but have NO token yet'));
  logger.divider();

  for (const round of rounds) {
    const potential = round.airdropPotential || { level: '?', score: 0, reasons: [] };
    const levelColor =
      potential.level === 'HIGH' ? chalk.red.bold :
      potential.level === 'MEDIUM' ? chalk.yellow :
      chalk.gray;

    console.log(
      `  ${chalk.bold(round.project)} ${levelColor(`[${potential.level}]`)} ` +
      `${chalk.cyan(round.amount)} ${chalk.gray(round.round)} ${chalk.gray(round.date)}`
    );

    if (round.tvl) {
      console.log(`    TVL: ${chalk.green(round.tvl)}`);
    }

    if (round.chains && round.chains.length > 0) {
      console.log(`    Chains: ${chalk.gray(round.chains.join(', '))}`);
    }

    if (round.leadInvestors && round.leadInvestors.length > 0) {
      console.log(`    Investors: ${chalk.gray(round.leadInvestors.join(', '))}`);
    }

    if (potential.reasons && potential.reasons.length > 0) {
      potential.reasons.forEach((reason) => {
        console.log(`    ${chalk.gray('+ ' + reason)}`);
      });
    }

    console.log('');
  }

  logger.divider();
}

module.exports = { refresh, loadCached, loadCachedFunding, display, displayFunding };
