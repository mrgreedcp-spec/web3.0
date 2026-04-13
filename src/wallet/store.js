const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const ALGORITHM = 'aes-256-gcm';
const KEY_LENGTH = 32;
const SALT_LENGTH = 32;
const IV_LENGTH = 16;

function deriveKey(password, salt) {
  return crypto.scryptSync(password, salt, KEY_LENGTH);
}

/**
 * Encrypt an array of private keys and save to file.
 */
function saveWallets(filePath, privateKeys, password) {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const salt = crypto.randomBytes(SALT_LENGTH);
  const iv = crypto.randomBytes(IV_LENGTH);
  const key = deriveKey(password, salt);

  const cipher = crypto.createCipheriv(ALGORITHM, key, iv);
  const plaintext = JSON.stringify(privateKeys);
  let encrypted = cipher.update(plaintext, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  const authTag = cipher.getAuthTag().toString('hex');

  const data = {
    salt: salt.toString('hex'),
    iv: iv.toString('hex'),
    authTag,
    encrypted,
  };

  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

/**
 * Load and decrypt private keys from file.
 * Returns an array of private key strings.
 */
function loadWallets(filePath, password) {
  if (!fs.existsSync(filePath)) {
    return null;
  }

  const raw = fs.readFileSync(filePath, 'utf8');
  const data = JSON.parse(raw);

  const salt = Buffer.from(data.salt, 'hex');
  const iv = Buffer.from(data.iv, 'hex');
  const authTag = Buffer.from(data.authTag, 'hex');
  const key = deriveKey(password, salt);

  const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
  decipher.setAuthTag(authTag);

  let decrypted = decipher.update(data.encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');

  return JSON.parse(decrypted);
}

/**
 * Check if wallet file exists.
 */
function walletsExist(filePath) {
  return fs.existsSync(filePath);
}

module.exports = { saveWallets, loadWallets, walletsExist };
