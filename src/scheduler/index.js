const cron = require('node-cron');
const config = require('../config');
const logger = require('../logger');
const faucets = require('../faucets');
const protocols = require('../protocols');
const tracker = require('../tracker');
const { sleep } = require('../faucets/utils');

const jobs = [];

/**
 * Add random jitter (0 to scheduleJitter minutes) before executing a task.
 */
async function withJitter(taskName, fn) {
  const jitterMs = Math.floor(Math.random() * config.scheduleJitter * 60 * 1000);
  logger.info(`[Scheduler] ${taskName} will start in ${Math.round(jitterMs / 60000)} minutes (jitter)`);
  await sleep(jitterMs);

  try {
    await fn();
  } catch (error) {
    logger.error(`[Scheduler] ${taskName} failed: ${error.message}`);
  }
}

/**
 * Start all scheduled jobs.
 */
function start() {
  logger.info('[Scheduler] Starting scheduled tasks...');

  // Faucet claiming schedule
  if (cron.validate(config.faucetSchedule)) {
    const faucetJob = cron.schedule(config.faucetSchedule, () => {
      withJitter('Faucet Claims', () => faucets.runAll());
    });
    jobs.push(faucetJob);
    logger.info(`[Scheduler] Faucet claims: ${config.faucetSchedule}`);
  } else {
    logger.error(`[Scheduler] Invalid faucet schedule: ${config.faucetSchedule}`);
  }

  // Protocol interactions schedule
  if (cron.validate(config.protocolSchedule)) {
    const protocolJob = cron.schedule(config.protocolSchedule, () => {
      withJitter('Protocol Interactions', () => protocols.runAll());
    });
    jobs.push(protocolJob);
    logger.info(`[Scheduler] Protocol interactions: ${config.protocolSchedule}`);
  } else {
    logger.error(`[Scheduler] Invalid protocol schedule: ${config.protocolSchedule}`);
  }

  // Tracker refresh schedule
  if (cron.validate(config.trackerSchedule)) {
    const trackerJob = cron.schedule(config.trackerSchedule, () => {
      withJitter('Airdrop Tracker', () => tracker.refresh());
    });
    jobs.push(trackerJob);
    logger.info(`[Scheduler] Airdrop tracker: ${config.trackerSchedule}`);
  } else {
    logger.error(`[Scheduler] Invalid tracker schedule: ${config.trackerSchedule}`);
  }

  logger.success(`[Scheduler] ${jobs.length} scheduled tasks registered`);

  // Graceful shutdown
  process.on('SIGINT', stop);
  process.on('SIGTERM', stop);
}

/**
 * Stop all scheduled jobs.
 */
function stop() {
  logger.info('[Scheduler] Stopping all tasks...');
  jobs.forEach((job) => job.stop());
  logger.info('[Scheduler] All tasks stopped. Goodbye!');
  process.exit(0);
}

module.exports = { start, stop };
