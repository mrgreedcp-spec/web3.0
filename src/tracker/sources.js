const axios = require('axios');
const logger = require('../logger');

/**
 * Known airdrop opportunity sources.
 * These are manually curated testnet projects that have hinted at airdrops.
 * Update this list as new opportunities emerge.
 */
const KNOWN_OPPORTUNITIES = [
  {
    project: 'Base',
    chain: 'base-sepolia',
    type: 'L2 Usage',
    description: 'Use Base testnet - bridge, swap, deploy contracts',
    status: 'active',
    estimatedValue: 'Unknown',
    requirements: ['Bridge ETH to Base', 'Use DEX on Base', 'Deploy contract'],
  },
  {
    project: 'Arbitrum Ecosystem',
    chain: 'arbitrum-sepolia',
    type: 'L2 Usage',
    description: 'Interact with Arbitrum Sepolia testnet protocols',
    status: 'active',
    estimatedValue: 'Unknown',
    requirements: ['Bridge ETH to Arbitrum', 'Swap on Uniswap', 'Deploy contract'],
  },
  {
    project: 'LayerZero / Cross-chain',
    chain: 'multi-chain',
    type: 'Bridge',
    description: 'Cross-chain bridging activity may qualify for future bridge protocol airdrops',
    status: 'speculative',
    estimatedValue: 'Unknown',
    requirements: ['Bridge between testnets', 'Use multiple chains'],
  },
  {
    project: 'Uniswap (Potential Future)',
    chain: 'sepolia',
    type: 'DEX',
    description: 'Testnet DEX activity on Uniswap V3',
    status: 'speculative',
    estimatedValue: 'Unknown',
    requirements: ['Perform swaps', 'Multiple token pairs'],
  },
];

/**
 * Fetch opportunities from a public aggregator API.
 * Falls back to local known list if API is unavailable.
 */
async function fetchOpportunities() {
  // Start with our known local opportunities
  const opportunities = [...KNOWN_OPPORTUNITIES];

  // Try to fetch from public data sources
  try {
    // DeFiLlama airdrops endpoint (if available)
    const response = await axios.get('https://api.llama.fi/protocols', {
      timeout: 10000,
    });

    if (response.data && Array.isArray(response.data)) {
      // Filter for protocols that are on our supported chains and have testnet activity
      const relevantProtocols = response.data
        .filter((p) => p.chains && (p.chains.includes('Ethereum') || p.chains.includes('Arbitrum') || p.chains.includes('Base')))
        .filter((p) => !p.symbol) // No token yet = potential airdrop
        .slice(0, 10)
        .map((p) => ({
          project: p.name,
          chain: 'multi-chain',
          type: 'DeFi Protocol',
          description: `${p.name} - no token yet, potential airdrop candidate`,
          status: 'speculative',
          estimatedValue: 'Unknown',
          requirements: ['Research and interact with testnet if available'],
        }));

      opportunities.push(...relevantProtocols);
    }
  } catch {
    logger.warn('[Tracker] Could not fetch external data, using local opportunities only');
  }

  return opportunities;
}

module.exports = { fetchOpportunities, KNOWN_OPPORTUNITIES };
