#!/usr/bin/env node
/**
 * Phase 0: Remove slop opportunities from dashboard
 * Removes 36 research-flagged IDs, archives them, and updates both HTML files
 */

const fs = require('fs');
const path = require('path');

// IDs marked as slop during research review
const SLOP_IDS = [
  'home-battery-backup-richmond-va',
  'stairlift-installation-hialeah-fl',
  'cybersecurity-consulting-madison-wi',
  'walk-in-tub-installation-goulburn-nsw',
  'epoxy-flooring-oxnard-ca',
  'walk-in-tub-installation-aurora-il',
  'trucking-accident-attorney-blue-mountains-nsw',
  'outdoor-kitchen-installation-ontario-ca',
  'basement-waterproofing-west-valley-city-ut',
  'commercial-snow-removal-salt-lake-city-ut',
  'walk-in-shower-miramar-fl',
  'solar-panel-installation-pasadena-tx',
  'bathroom-accessibility-remodel-olathe-ks',
  'outdoor-kitchen-installation-st.-paul-mn',
  'solar-panel-installation-newport-news-va',
  'employment-law-attorney-stockton-ca',
  'workers-comp-attorney-warren-mi',
  'hurricane-shutter-installation-central-coast-nsw',
  'home-elevator-installation-norwalk-ca',
  'home-theater-installation-tallahassee-fl',
  'security-camera-installation-broken-arrow-ok',
  'outdoor-kitchen-installation-costa-mesa-ca',
  'impact-window-installation-palmerston-nt',
  'security-camera-installation-modesto-ca',
  'fire-alarm-installation-north-las-vegas-nv',
  'home-elevator-installation-worcester-ma',
  'ice-dam-removal-katherine-nt',
  'workers-comp-attorney-santa-ana-ca',
  'employment-law-attorney-augusta-ga',
  'veterans-benefits-attorney-sunshine-coast-qld',
  'employment-law-attorney-victorville-ca',
  'cybersecurity-consulting-palmerston-nt',
  'home-elevator-victor-harbor-sa',
  'home-battery-backup-denton-tx',
  'walk-in-shower-columbia-mo',
  'home-battery-backup-moreno-valley-ca'
];

const WORKSPACE = process.cwd();
const INDEX_PATH = path.join(WORKSPACE, 'index.html');
const DASHBOARD_PATH = path.join(WORKSPACE, 'dashboard.html');
const ARCHIVE_PATH = path.join(WORKSPACE, 'killed', 'slop-phase0.json');

function processHtmlFile(filePath) {
  console.log(`\nProcessing ${path.basename(filePath)}...`);
  
  const html = fs.readFileSync(filePath, 'utf8');
  const match = html.match(/const OPPORTUNITIES_DATA = ({.*?});/s);
  
  if (!match) {
    throw new Error(`Could not find OPPORTUNITIES_DATA in ${filePath}`);
  }
  
  const data = JSON.parse(match[1]);
  const originalCount = data.opportunities.length;
  
  console.log(`  Original count: ${originalCount}`);
  
  // Separate slop from keep
  const slopOpportunities = [];
  const keepOpportunities = [];
  
  const slopSet = new Set(SLOP_IDS);
  const seenIds = new Set();
  
  for (const opp of data.opportunities) {
    // Check for duplicates
    if (seenIds.has(opp.id)) {
      console.log(`  ⚠️  Duplicate found: ${opp.id}`);
      // Skip duplicate
      continue;
    }
    seenIds.add(opp.id);
    
    if (slopSet.has(opp.id)) {
      slopOpportunities.push(opp);
    } else {
      keepOpportunities.push(opp);
    }
  }
  
  console.log(`  Removed: ${slopOpportunities.length}`);
  console.log(`  Kept: ${keepOpportunities.length}`);
  console.log(`  Deduped: ${originalCount - slopOpportunities.length - keepOpportunities.length}`);
  
  // Update data
  data.opportunities = keepOpportunities;
  data.count = keepOpportunities.length;
  data.generated_at = new Date().toISOString().split('T')[0];
  
  // Replace in HTML (preserve formatting)
  const updatedData = JSON.stringify(data);
  const updatedHtml = html.replace(
    /const OPPORTUNITIES_DATA = {.*?};/s,
    `const OPPORTUNITIES_DATA = ${updatedData};`
  );
  
  fs.writeFileSync(filePath, updatedHtml, 'utf8');
  console.log(`  ✓ Updated ${path.basename(filePath)}`);
  
  return { originalCount, slopOpportunities, keepCount: keepOpportunities.length };
}

function main() {
  console.log('═══════════════════════════════════════════════════');
  console.log('Phase 0: Slop Removal');
  console.log('═══════════════════════════════════════════════════');
  
  // Process index.html
  const indexResult = processHtmlFile(INDEX_PATH);
  
  // Process dashboard.html (check if it has embedded data)
  let dashboardResult = null;
  const dashboardHtml = fs.readFileSync(DASHBOARD_PATH, 'utf8');
  if (dashboardHtml.includes('const OPPORTUNITIES_DATA')) {
    dashboardResult = processHtmlFile(DASHBOARD_PATH);
  } else {
    console.log('\nℹ️  dashboard.html has no embedded data (OK - uses generator)');
  }
  
  // Create archive
  console.log('\nCreating archive...');
  const archive = {
    removed_at: new Date().toISOString(),
    reason: 'phase0-slop-purge',
    description: 'Research review identified fake perfect scores, geo/legal mismatches, and template junk',
    count: indexResult.slopOpportunities.length,
    ids: SLOP_IDS,
    opportunities: indexResult.slopOpportunities
  };
  
  fs.writeFileSync(ARCHIVE_PATH, JSON.stringify(archive, null, 2), 'utf8');
  console.log(`  ✓ Archive saved: ${ARCHIVE_PATH}`);
  console.log(`  Archived ${archive.count} opportunities`);
  
  // Summary
  console.log('\n═══════════════════════════════════════════════════');
  console.log('Summary:');
  console.log(`  Before: ${indexResult.originalCount} opportunities`);
  console.log(`  After:  ${indexResult.keepCount} opportunities`);
  console.log(`  Removed: ${indexResult.slopOpportunities.length} slop cards`);
  console.log('═══════════════════════════════════════════════════');
  console.log('✓ Phase 0 complete!');
}

main();
