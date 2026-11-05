// Publishes every jar in release/<version>/ to Modrinth and CurseForge, and refreshes the Modrinth listing.
// Run by .github/workflows/publish.yml; also works locally with the same environment variables:
//
//   MODRINTH_TOKEN=... CURSEFORGE_TOKEN=... VERSION=1.0.0 node scripts/publish.mjs
//
// Each jar is one target (see TARGETS). A target that is already on a site is skipped, so a rerun only uploads
// what is missing. ONLY=fabric-26.2,forge-1.20.1 limits a run to some targets.
// Optional: CHANGELOG_FILE (default patchnotes/<version>.md), DRY_RUN=true, SKIP_MODRINTH=true, SKIP_CURSEFORGE=true,
// UPDATE_LISTING=false (Modrinth description, summary and icon), UPLOAD_GALLERY=false (Modrinth gallery).
// The CurseForge upload API cannot change a project's description or images, so those are pasted in by hand
// from marketing/ (see marketing/README.md).
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const env = process.env;
const flag = (name, fallback) => (env[name] === undefined || env[name] === '' ? fallback : env[name] === 'true');

// No defaults on purpose: a wrong id would publish Bunnyland into someone else's project.
const MODRINTH_ID = env.MODRINTH_ID || '';
const CURSEFORGE_ID = env.CURSEFORGE_ID || '';
// Refuse to touch a project whose name does not look like Bunnyland.
const looksLikeBunnyland = (...names) => names.some((n) => /bunny/i.test(n || ''));
const TITLE = 'Bunnyland';
const UA = 'MeherBenSalem/Bunnyland publish script (github.com/MeherBenSalem/Bunnyland)';

const DRY_RUN = flag('DRY_RUN', false);
const SKIP_MODRINTH = flag('SKIP_MODRINTH', false);
const SKIP_CURSEFORGE = flag('SKIP_CURSEFORGE', false);
const UPDATE_LISTING = flag('UPDATE_LISTING', true);
const UPLOAD_GALLERY = flag('UPLOAD_GALLERY', true);

const version = (env.VERSION || '').replace(/^v/, '');
if (!version) throw new Error('Set VERSION, e.g. 1.0.0');
// [loader, Minecraft, Java]. The jar is release/<version>/bunnyland-<loader>-<minecraft>-<version>.jar.
const TARGETS = [
  ['forge', '1.20.1', 17], ['fabric', '1.20.1', 17],
  ['neoforge', '1.21.1', 21], ['fabric', '1.21.1', 21],
  ['neoforge', '26.2', 25], ['fabric', '26.2', 25],
  ['neoforge', '26.3', 25], ['fabric', '26.3', 25],
].map(([loader, minecraft, java]) => {
  const jar = path.join(ROOT, 'release', version, `bunnyland-${loader}-${minecraft}-${version}.jar`);
  return { key: `${loader}-${minecraft}`, loader, minecraft, java, jar, jarName: path.basename(jar) };
}).filter((t) => !env.ONLY || env.ONLY.split(',').includes(t.key));
for (const t of TARGETS) if (!fs.existsSync(t.jar)) throw new Error(`No jar at ${t.jar}`);
// Targets to leave out on one site, e.g. CURSEFORGE_SKIP=fabric-1.20.1 for a file uploaded by hand.
const skipOn = (name) => (env[name] || '').split(',').map((x) => x.trim()).filter(Boolean);
const LOADER_NAME = { forge: 'Forge', fabric: 'Fabric', neoforge: 'NeoForge' };
const changelogFile = path.resolve(ROOT, env.CHANGELOG_FILE || `patchnotes/${version}.md`);
const changelog = fs.existsSync(changelogFile)
  ? fs.readFileSync(changelogFile, 'utf8')
  : `## ${TITLE} ${version}\n\nSee https://github.com/MeherBenSalem/Bunnyland`;

const marketing = path.join(ROOT, 'marketing');
// Modrinth gallery, in listing order. The first one is featured (shown in search results).
const GALLERY = [
  ['cherry-grove.jpg', 'A cherry grove', 'Bunnies, a fox, a kitty, a bird and a butterfly among the petals'],
  ['dress-up.jpg', 'Dress-up', 'Collars, bows, hats, glasses and a scarf, fitted to every creature'],
  ['rare-variants.jpg', 'Rare variants', 'Rare variants are born only by breeding'],
  ['moonlit-night.jpg', 'Moonlit night', 'Moon Bunnies and Moon Deer glow after dark'],
  ['snowy-taiga.jpg', 'Snowy taiga', 'Snowball Bunnies on a frozen lake'],
  ['river.jpg', 'River', 'A Tiny Swan family and two Pastel Axolotls'],
  ['forest.jpg', 'Forest', 'A Honey Bear by a beehive, a Strawberry Bunny and a Strawberry Mouse'],
  ['beds-and-bowls.jpg', 'Pet beds and bowls', 'Pets napping in their beds next to their feeding bowls'],
  ['variants-cotton-bunny.jpg', 'Cotton Bunny variants', 'Every Cotton Bunny colourway'],
  ['variants-axolotl.jpg', 'Pastel Axolotl variants', 'Every Pastel Axolotl colourway'],
  ['befriend.jpg', 'Befriending', 'A Bunny Biscuit wins over a Cotton Bunny'],
  ['petting.jpg', 'Petting', 'Petting a pet shows how it feels'],
  ['journal-index.jpg', 'Pet Journal', 'The journal counts every creature you discover and befriend'],
  ['journal-cotton-bunny.jpg', 'Pet Journal: Cotton Bunny', 'A creature page with its habitat, treat and favourite foods'],
  ['journal-honey-bear.jpg', 'Pet Journal: Honey Bear', 'A creature page with its variants'],
];

async function call(what, url, options = {}, okStatuses = []) {
  for (let attempt = 1; attempt <= 4; attempt++) {
    const res = await fetch(url, { ...options, headers: { 'User-Agent': UA, ...(options.headers || {}) } });
    if (res.ok || okStatuses.includes(res.status)) return res;
    const text = await res.text();
    if ((res.status === 429 || res.status >= 500) && attempt < 4) {
      console.warn(`${what}: ${res.status}, retrying (${attempt})`);
      await new Promise((r) => setTimeout(r, 10000 * attempt));
      continue;
    }
    throw new Error(`${what}: ${res.status} ${text.slice(0, 600)}`);
  }
}

// ---------------------------------------------------------------- Modrinth

async function modrinth() {
  const token = env.MODRINTH_TOKEN;
  if (!token) throw new Error('MODRINTH_TOKEN is not set');
  const api = 'https://api.modrinth.com/v2';
  const auth = { Authorization: token };

  if (!MODRINTH_ID) throw new Error('MODRINTH_ID is not set');
  const project = await (await call('Modrinth project', `${api}/project/${MODRINTH_ID}`, { headers: auth })).json();
  console.log(`Modrinth project: ${project.title} (${project.slug}, ${project.status})`);
  if (!looksLikeBunnyland(project.title, project.slug)) {
    throw new Error(`Modrinth project ${MODRINTH_ID} is "${project.title}", not Bunnyland; refusing to publish to it`);
  }

  if (UPDATE_LISTING) {
    const body = fs.readFileSync(path.join(marketing, 'curseforge', 'description.md'), 'utf8');
    const summary = fs.readFileSync(path.join(marketing, 'curseforge', 'summary.txt'), 'utf8').trim();
    if (DRY_RUN) console.log(`[dry-run] Modrinth listing: summary ${summary.length} chars, body ${body.length} chars, icon`);
    else {
      await call('Modrinth listing', `${api}/project/${MODRINTH_ID}`, {
        method: 'PATCH', headers: { ...auth, 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: summary, body }),
      });
      await call('Modrinth icon', `${api}/project/${MODRINTH_ID}/icon?ext=png`, {
        method: 'PATCH', headers: { ...auth, 'Content-Type': 'image/png' },
        body: fs.readFileSync(path.join(marketing, 'images', 'icon.png')),
      });
      console.log('Modrinth listing updated (summary, description, icon)');
    }
  }

  if (UPLOAD_GALLERY) {
    const have = new Set((project.gallery || []).map((g) => g.title));
    for (const [i, [file, title, description]] of GALLERY.entries()) {
      if (have.has(title)) { console.log(`Modrinth gallery: "${title}" already there`); continue; }
      if (DRY_RUN) { console.log(`[dry-run] Modrinth gallery: ${file}`); continue; }
      const query = new URLSearchParams({ ext: 'jpg', featured: String(i === 0), title, description, ordering: String(i) });
      await call(`Modrinth gallery ${file}`, `${api}/project/${MODRINTH_ID}/gallery?${query}`, {
        method: 'POST', headers: { ...auth, 'Content-Type': 'image/jpeg' },
        body: fs.readFileSync(path.join(marketing, 'images', 'screenshots', file)),
      });
      console.log(`Modrinth gallery: added "${title}"`);
    }
  }

  const versions = await (await call('Modrinth versions', `${api}/project/${MODRINTH_ID}/version`, { headers: auth })).json();
  const geckolib = await (await call('Modrinth GeckoLib', `${api}/project/geckolib`)).json();
  const fabricApi = await (await call('Modrinth Fabric API', `${api}/project/fabric-api`)).json();
  const failed = [];
  for (const t of TARGETS) {
    if (skipOn('MODRINTH_SKIP').includes(t.key)) { console.log(`Modrinth: skipping ${t.key} (MODRINTH_SKIP)`); continue; }
    const number = `${version}+${t.loader}-${t.minecraft}`;
    if (versions.some((v) => v.version_number === number || (v.version_number.startsWith(version)
        && v.loaders.includes(t.loader) && v.game_versions.includes(t.minecraft)))) {
      console.log(`Modrinth already has ${version} for ${t.key}; skipping`);
      continue;
    }
    const dependencies = [{ project_id: geckolib.id, dependency_type: 'required' }];
    if (t.loader === 'fabric') dependencies.push({ project_id: fabricApi.id, dependency_type: 'required' });
    const data = {
      name: `${TITLE} ${version} (${LOADER_NAME[t.loader]} ${t.minecraft})`,
      version_number: number,
      changelog,
      dependencies,
      game_versions: [t.minecraft],
      version_type: 'release',
      loaders: [t.loader],
      featured: true,
      status: 'listed',
      project_id: MODRINTH_ID,
      file_parts: ['file_0'],
      primary_file: 'file_0',
    };
    if (DRY_RUN) { console.log(`[dry-run] Modrinth version ${t.key}`, { ...data, changelog: `${changelog.length} chars` }); continue; }
    try {
      const form = new FormData();
      form.append('data', JSON.stringify(data));
      form.append('file_0', new Blob([fs.readFileSync(t.jar)]), t.jarName);
      const created = await (await call(`Modrinth version ${t.key}`, `${api}/version`, { method: 'POST', headers: auth, body: form })).json();
      console.log(`Modrinth OK ${t.key}: https://modrinth.com/mod/${project.slug}/version/${created.id}`);
    } catch (error) { console.error(error.message); failed.push(t.key); }
  }
  if (failed.length) throw new Error(`targets ${failed.join(', ')}`);
}

// ---------------------------------------------------------------- CurseForge

async function curseforge() {
  const token = env.CURSEFORGE_TOKEN;
  if (!token) throw new Error('CURSEFORGE_TOKEN is not set');
  if (!CURSEFORGE_ID) throw new Error('CURSEFORGE_ID is not set');
  const page = await call('CurseForge project page', `https://www.curseforge.com/projects/${CURSEFORGE_ID}`, { redirect: 'follow' }, [403]);
  if (page.status !== 403) {
    const finalUrl = page.url;
    const title = ((await page.text()).match(/<title>([^<]*)<\/title>/) || [])[1] || '';
    console.log(`CurseForge project: ${title.trim()} (${finalUrl})`);
    if (!looksLikeBunnyland(title, finalUrl)) {
      throw new Error(`CurseForge project ${CURSEFORGE_ID} is "${title.trim()}" (${finalUrl}), not Bunnyland; refusing to publish to it`);
    }
  } else if (env.CURSEFORGE_ID_CONFIRMED !== 'true') {
    throw new Error(`Could not read CurseForge project ${CURSEFORGE_ID} to check it is Bunnyland; set CURSEFORGE_ID_CONFIRMED=true to skip the check`);
  }
  const api = 'https://minecraft.curseforge.com/api';
  const auth = { 'X-Api-Token': token };
  const types = await (await call('CurseForge version types', `${api}/game/version-types`, { headers: auth })).json();
  const all = await (await call('CurseForge versions', `${api}/game/versions`, { headers: auth })).json();
  const typeId = (slug) => {
    const t = types.find((x) => x.slug === slug);
    if (!t) throw new Error(`No CurseForge version type "${slug}"`);
    return t.id;
  };
  const versionId = (typeSlug, name) => {
    const hit = all.find((v) => v.gameVersionTypeID === typeId(typeSlug) && v.name === name);
    if (!hit) throw new Error(`No CurseForge version "${name}" of type "${typeSlug}"`);
    return hit.id;
  };
  // Minecraft versions sit in one type per minor version (minecraft-1-20, minecraft-26-2, ...); match by name.
  const minecraftTypes = new Set(types.filter((x) => x.slug.startsWith('minecraft-')).map((x) => x.id));
  const mcId = (name) => {
    const hit = all.find((v) => minecraftTypes.has(v.gameVersionTypeID) && v.name === name);
    if (!hit) throw new Error(`No CurseForge Minecraft version "${name}"`);
    return hit.id;
  };
  const optionalId = (typeSlug, name) => {
    try { return versionId(typeSlug, name); } catch (error) { console.warn(`${error.message}; leaving it out`); return null; }
  };
  const existing = await (await call('CurseForge project files', `https://api.curseforge.com/v1/mods/${CURSEFORGE_ID}/files?pageSize=50`,
    { headers: { 'x-api-key': env.CURSEFORGE_CORE_KEY || '' } }, [401, 403, 404])).json().catch(() => ({}));
  const have = new Set((existing.data || []).map((f) => f.fileName));
  const failed = [];
  for (const t of TARGETS) {
    if (have.has(t.jarName)) { console.log(`CurseForge already has ${t.jarName}; skipping`); continue; }
    if (skipOn('CURSEFORGE_SKIP').includes(t.key)) { console.log(`CurseForge: skipping ${t.key} (CURSEFORGE_SKIP)`); continue; }
    try {
      const gameVersions = [
        mcId(t.minecraft),
        versionId('modloader', LOADER_NAME[t.loader]),
        optionalId('environment', 'Client'),
        optionalId('environment', 'Server'),
        optionalId('java', `Java ${t.java}`),
      ].filter((id) => id !== null);
      const projects = [{ slug: 'geckolib', type: 'requiredDependency' }];
      if (t.loader === 'fabric') projects.push({ slug: 'fabric-api', type: 'requiredDependency' });
      const metadata = {
        changelog,
        changelogType: 'markdown',
        displayName: `${TITLE} ${version} (${LOADER_NAME[t.loader]} ${t.minecraft})`,
        gameVersions,
        releaseType: 'release',
        relations: { projects },
      };
      if (DRY_RUN) { console.log(`[dry-run] CurseForge file ${t.key}`, { ...metadata, changelog: `${changelog.length} chars` }); continue; }
      const form = new FormData();
      form.append('metadata', JSON.stringify(metadata));
      form.append('file', new Blob([fs.readFileSync(t.jar)]), t.jarName);
      const res = await call(`CurseForge upload ${t.key}`, `${api}/projects/${CURSEFORGE_ID}/upload-file`, { method: 'POST', headers: auth, body: form });
      const { id } = await res.json();
      console.log(`CurseForge OK ${t.key}: file ${id} on project ${CURSEFORGE_ID}`);
    } catch (error) { console.error(error.message); failed.push(t.key); }
  }
  if (failed.length) throw new Error(`targets ${failed.join(', ')}`);
}

console.log(`Publishing ${TITLE} ${version}: ${TARGETS.map((t) => t.key).join(', ')}${DRY_RUN ? ' [dry run]' : ''}`);
const failures = [];
for (const [name, run, skip] of [['Modrinth', modrinth, SKIP_MODRINTH], ['CurseForge', curseforge, SKIP_CURSEFORGE]]) {
  if (skip) { console.log(`Skipping ${name}`); continue; }
  try { await run(); } catch (error) { console.error(`${name} failed: ${error.message}`); failures.push(name); }
}
if (failures.length) { console.error(`Failed: ${failures.join(', ')}`); process.exit(1); }
