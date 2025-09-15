#!/usr/bin/env node
/**
 * Generate build info for the frontend
 */
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function getGitCommit() {
  try {
    return execSync('git rev-parse HEAD', { encoding: 'utf8' }).trim();
  } catch (error) {
    return 'unknown';
  }
}

function getGitBranch() {
  try {
    return execSync('git rev-parse --abbrev-ref HEAD', { encoding: 'utf8' }).trim();
  } catch (error) {
    return 'unknown';
  }
}

function generateBuildInfo() {
  return {
    version: process.env.BUILD_VERSION || 'dev',
    buildNumber: process.env.BUILD_NUMBER || 'local',
    gitCommit: process.env.GIT_COMMIT || getGitCommit(),
    gitBranch: getGitBranch(),
    environment: process.env.ENVIRONMENT || process.env.NODE_ENV || 'development',
    buildTime: new Date().toISOString(),
    service: 'frontend'
  };
}

function main() {
  const buildInfo = generateBuildInfo();

  // Ensure public directory exists
  const publicDir = path.join(__dirname, 'public');
  if (!fs.existsSync(publicDir)) {
    fs.mkdirSync(publicDir, { recursive: true });
  }

  // Write to build-info.json
  const buildInfoPath = path.join(publicDir, 'build-info.json');
  fs.writeFileSync(buildInfoPath, JSON.stringify(buildInfo, null, 2));

  console.log(`✅ Build info generated: ${buildInfoPath}`);
  console.log(JSON.stringify(buildInfo, null, 2));
}

// Run main function if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { generateBuildInfo };