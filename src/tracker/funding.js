const axios = require('axios');
const logger = require('../logger');

/**
 * Fetch recent Web3 funding rounds from public sources.
 * Focuses on projects that:
 * - Raised significant funding ($5M+)
 * - Don't have a token yet
 * - Have testnet or early-stage products
 */
async function fetchFundingRounds() {
  const results = [];

  // Source 1: DeFiLlama raises endpoint
  try {
    logger.info('[Funding] Fetching from DeFiLlama raises...');
    const response = await axios.get('https://api.llama.fi/raises', {
      timeout: 15000,
    });

    if (response.data && response.data.raises) {
      const now = Date.now();
      const sixMonthsAgo = now - 180 * 24 * 60 * 60 * 1000;

      const recent = response.data.raises
        .filter((r) => {
          const raiseDate = r.date ? r.date * 1000 : 0;
          return raiseDate > sixMonthsAgo;
        })
        .filter((r) => {
          // Focus on larger raises - more likely to launch token
          const amount = parseFloat(r.amount) || 0;
          return amount >= 5;  // $5M+
        })
        .sort((a, b) => (b.date || 0) - (a.date || 0))
        .slice(0, 30);

      for (const raise of recent) {
        results.push({
          source: 'DeFiLlama',
          project: raise.name || 'Unknown',
          amount: raise.amount ? `$${raise.amount}M` : 'Undisclosed',
          round: raise.round || 'Unknown',
          date: raise.date ? new Date(raise.date * 1000).toISOString().split('T')[0] : 'Unknown',
          category: raise.category || 'Unknown',
          chains: raise.chains || [],
          leadInvestors: raise.leadInvestors || [],
          hasToken: false, // Projects in raises typically don't have tokens yet
          airdropPotential: calculateAirdropPotential(raise),
        });
      }

      logger.success(`[Funding] Found ${results.length} recent funding rounds ($5M+)`);
    }
  } catch (error) {
    logger.warn(`[Funding] DeFiLlama fetch failed: ${error.message}`);
  }

  // Source 2: DeFiLlama protocols without tokens
  try {
    logger.info('[Funding] Checking protocols without tokens...');
    const response = await axios.get('https://api.llama.fi/protocols', {
      timeout: 15000,
    });

    if (response.data && Array.isArray(response.data)) {
      const noTokenProtocols = response.data
        .filter((p) => !p.symbol && !p.gecko_id) // No token
        .filter((p) => p.tvl && p.tvl > 1000000) // TVL > $1M = real usage
        .sort((a, b) => (b.tvl || 0) - (a.tvl || 0))
        .slice(0, 15);

      for (const protocol of noTokenProtocols) {
        // Check if already in results (from funding)
        const exists = results.some(
          (r) => r.project.toLowerCase() === (protocol.name || '').toLowerCase()
        );

        if (!exists) {
          results.push({
            source: 'DeFiLlama-protocols',
            project: protocol.name,
            amount: 'N/A',
            round: 'N/A',
            date: 'N/A',
            category: protocol.category || 'DeFi',
            chains: protocol.chains || [],
            leadInvestors: [],
            hasToken: false,
            tvl: protocol.tvl ? `$${(protocol.tvl / 1000000).toFixed(1)}M` : 'Unknown',
            airdropPotential: calculateProtocolPotential(protocol),
          });
        }
      }
    }
  } catch (error) {
    logger.warn(`[Funding] Protocol fetch failed: ${error.message}`);
  }

  // Sort by airdrop potential
  results.sort((a, b) => b.airdropPotential.score - a.airdropPotential.score);

  return results;
}

/**
 * Calculate airdrop potential score for a funding round.
 * Higher score = more likely to airdrop.
 */
function calculateAirdropPotential(raise) {
  let score = 0;
  const reasons = [];

  // Factor 1: Funding amount (larger = more likely to launch token)
  const amount = parseFloat(raise.amount) || 0;
  if (amount >= 50) {
    score += 30;
    reasons.push('Mega round ($50M+)');
  } else if (amount >= 20) {
    score += 25;
    reasons.push('Large round ($20M+)');
  } else if (amount >= 10) {
    score += 20;
    reasons.push('Medium round ($10M+)');
  } else if (amount >= 5) {
    score += 10;
    reasons.push('Seed/Early round ($5M+)');
  }

  // Factor 2: Top-tier investors
  const topInvestors = [
    'a16z', 'paradigm', 'polychain', 'sequoia', 'binance',
    'coinbase', 'dragonfly', 'multicoin', 'pantera', 'framework',
  ];
  const investors = (raise.leadInvestors || []).map((i) => (i || '').toLowerCase());
  const hasTopInvestor = investors.some((inv) =>
    topInvestors.some((top) => inv.includes(top))
  );
  if (hasTopInvestor) {
    score += 20;
    reasons.push('Top-tier investor(s)');
  }

  // Factor 3: Category (DeFi/L2/Bridge more likely to airdrop)
  const highAirdropCategories = ['dexes', 'lending', 'bridge', 'chain', 'l2', 'cross-chain'];
  if (highAirdropCategories.some((c) => (raise.category || '').toLowerCase().includes(c))) {
    score += 15;
    reasons.push('High-airdrop category');
  }

  // Factor 4: Recency (more recent = more relevant)
  const now = Date.now();
  const raiseDate = raise.date ? raise.date * 1000 : 0;
  const monthsAgo = (now - raiseDate) / (30 * 24 * 60 * 60 * 1000);
  if (monthsAgo < 3) {
    score += 15;
    reasons.push('Very recent (<3 months)');
  } else if (monthsAgo < 6) {
    score += 10;
    reasons.push('Recent (3-6 months)');
  }

  // Factor 5: Has chains info (means on-chain product exists)
  if (raise.chains && raise.chains.length > 0) {
    score += 10;
    reasons.push('On-chain product');
  }

  const level = score >= 60 ? 'HIGH' : score >= 35 ? 'MEDIUM' : 'LOW';

  return { score, level, reasons };
}

/**
 * Calculate airdrop potential for a protocol without token.
 */
function calculateProtocolPotential(protocol) {
  let score = 0;
  const reasons = [];

  // High TVL without token = strong airdrop candidate
  const tvl = protocol.tvl || 0;
  if (tvl > 100000000) {
    score += 40;
    reasons.push('Very high TVL ($100M+) without token');
  } else if (tvl > 10000000) {
    score += 30;
    reasons.push('High TVL ($10M+) without token');
  } else if (tvl > 1000000) {
    score += 20;
    reasons.push('Significant TVL ($1M+) without token');
  }

  // Multi-chain = higher likelihood
  if (protocol.chains && protocol.chains.length > 2) {
    score += 15;
    reasons.push('Multi-chain presence');
  }

  // Category
  const highCategories = ['dexes', 'lending', 'bridge', 'derivatives'];
  if (highCategories.some((c) => (protocol.category || '').toLowerCase().includes(c))) {
    score += 15;
    reasons.push('High-airdrop category');
  }

  const level = score >= 50 ? 'HIGH' : score >= 25 ? 'MEDIUM' : 'LOW';

  return { score, level, reasons };
}

module.exports = { fetchFundingRounds, calculateAirdropPotential };
