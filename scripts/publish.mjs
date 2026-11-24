// Publishes the 8 Bunnyland jars of one version to CurseForge. NightBeam publishes to CurseForge only (since 24 Nov
// 2026); the existing Modrinth project stays up as it is but gets no new versions.
// Run by .github/workflows/publish.yml (after the same-day guard); also works locally with the same environment variables:
//
//   CURSEFORGE_TOKEN=... CURSEFORGE_API_KEY=... CURSEFORGE_ID=1784884 \
//     VERSION=1.0.1 JAR_DIR=releases node scripts/publish.mjs
//
// Each jar is one target (see TARGETS). A target that is already on CurseForge is skipped, so a rerun only uploads
// what is missing. ONLY=fabric-26.2,forge-1.20.1 limits a run to some targets.
// Optional: JAR_DIR (default release/<version>), CHANGELOG_FILE (default patchnotes/<version>.md), DRY_RUN=true,
// CURSEFORGE_SKIP=<targets>, OFFLINE=true (print what would be sent and stop: no network, no tokens).
// The CurseForge upload API cannot change a project's description or images, so those are pasted in by hand
// from marketing/ (see marketing/README.md).
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const env = process.env;
const flag = (name, fallback) => (env[name] === undefined || env[name] === '' ? fallback : env[name] === 'true');

// No defaults on purpose: a wrong id would publish Bunnyland into someone else's project.
const CURSEFORGE_ID = env.CURSEFORGE_ID || '';
// Refuse to touch a project whose name does not look like Bunnyland.
const looksLikeBunnyland = (...names) => names.some((n) => /bunny/i.test(n || ''));
const TITLE = 'Bunnyland';
const UA = 'MeherBenSalem/Bunnyland publish script (github.com/MeherBenSalem/Bunnyland)';

const DRY_RUN = flag('DRY_RUN', false);
const OFFLINE = flag('OFFLINE', false);
// CurseForge Core API key (read-only): the existing-files check and the project name check.
const CURSEFORGE_API_KEY = env.CURSEFORGE_API_KEY || env.CURSEFORGE_CORE_KEY || '';
// 1784884 was checked by hand to be Bunny Land (it is also the publish workflow's fallback ID); curseforge.com
// blocks the page check from Actions, so when neither the Core API nor the page can name the project, only this
// ID is accepted unchecked.
const CURSEFORGE_ID_CHECKED = '1784884';

const version = (env.VERSION || '').replace(/^v/, '');
if (!version) throw new Error('Set VERSION, e.g. 1.0.0');
const JAR_DIR = path.resolve(ROOT, env.JAR_DIR || path.join('release', version));
// [loader, Minecraft, Java]: the 8 NightBeam convention targets. The jar is <JAR_DIR>/bunnyland-<loader>-<minecraft>-<version>.jar.
const TARGETS = [
  ['forge', '1.20.1', 17], ['fabric', '1.20.1', 17],
  ['neoforge', '1.21.1', 21], ['fabric', '1.21.1', 21],
  ['neoforge', '26.2', 25], ['fabric', '26.2', 25],
  ['neoforge', '26.3', 25], ['fabric', '26.3', 25],
].map(([loader, minecraft, java]) => {
  const jar = path.join(JAR_DIR, `bunnyland-${loader}-${minecraft}-${version}.jar`);
  return { key: `${loader}-${minecraft}`, loader, minecraft, java, jar, jarName: path.basename(jar) };
}).filter((t) => !env.ONLY || env.ONLY.split(',').includes(t.key));
for (const t of TARGETS) if (!fs.existsSync(t.jar)) throw new Error(`No jar at ${t.jar}`);
// Targets to leave out, e.g. CURSEFORGE_SKIP=fabric-1.20.1 for a file uploaded by hand.
const skipOn = (name) => (env[name] || '').split(',').map((x) => x.trim()).filter(Boolean);
const LOADER_NAME = { forge: 'Forge', fabric: 'Fabric', neoforge: 'NeoForge' };
const changelogFile = path.resolve(ROOT, env.CHANGELOG_FILE || `patchnotes/${version}.md`);
const changelog = fs.existsSync(changelogFile)
  ? fs.readFileSync(changelogFile, 'utf8')
  : `## ${TITLE} ${version}\n\nSee https://github.com/MeherBenSalem/Bunnyland`;

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

// ---------------------------------------------------------------- CurseForge

async function curseforge() {
  const token = env.CURSEFORGE_TOKEN;
  if (!token) throw new Error('CURSEFORGE_TOKEN is not set');
  if (!CURSEFORGE_ID) throw new Error('CURSEFORGE_ID is not set');
  // The Core API names the project; it is not blocked from Actions the way curseforge.com is. A project still in
  // moderation may not be readable there yet, which falls back to the page check below.
  const core = CURSEFORGE_API_KEY
    ? await call('CurseForge project', `https://api.curseforge.com/v1/mods/${CURSEFORGE_ID}`,
      { headers: { 'x-api-key': CURSEFORGE_API_KEY } }, [403, 404])
    : null;
  if (core && core.ok) {
    const mod = (await core.json()).data || {};
    console.log(`CurseForge project: ${mod.name} (${mod.slug})`);
    if (!looksLikeBunnyland(mod.name, mod.slug)) {
      throw new Error(`CurseForge project ${CURSEFORGE_ID} is "${mod.name}" (${mod.slug}), not Bunnyland; refusing to publish to it`);
    }
  } else {
    const page = await call('CurseForge project page', `https://www.curseforge.com/projects/${CURSEFORGE_ID}`, { redirect: 'follow' }, [403]);
    if (page.status !== 403) {
      const finalUrl = page.url;
      const title = ((await page.text()).match(/<title>([^<]*)<\/title>/) || [])[1] || '';
      console.log(`CurseForge project: ${title.trim()} (${finalUrl})`);
      if (!looksLikeBunnyland(title, finalUrl)) {
        throw new Error(`CurseForge project ${CURSEFORGE_ID} is "${title.trim()}" (${finalUrl}), not Bunnyland; refusing to publish to it`);
      }
    } else if (CURSEFORGE_ID !== CURSEFORGE_ID_CHECKED) {
      throw new Error(`Could not read CurseForge project ${CURSEFORGE_ID} to check it is Bunnyland (Core API: ${core ? core.status : 'no CURSEFORGE_API_KEY'})`);
    }
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
    { headers: { 'x-api-key': CURSEFORGE_API_KEY } }, [401, 403, 404])).json().catch(() => ({}));
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

// OFFLINE=true: what CurseForge would get, from the jar names alone. No tokens, no network (CI and dry-run previews).
function plan() {
  console.log(`[offline] ${TITLE} ${version} from ${path.relative(ROOT, JAR_DIR) || '.'}, changelog ${changelog.length} chars`);
  for (const t of TARGETS) {
    const deps = ['geckolib', ...(t.loader === 'fabric' ? ['fabric-api'] : [])].join(' + ');
    const site = skipOn('CURSEFORGE_SKIP').includes(t.key) ? 'skipped (CURSEFORGE_SKIP)' : `CurseForge (Java ${t.java})`;
    console.log(`[offline] ${t.jarName}: ${LOADER_NAME[t.loader]} ${t.minecraft}, requires ${deps}; ${site}`);
  }
}

if (OFFLINE) { plan(); process.exit(0); }
console.log(`Publishing ${TITLE} ${version}: ${TARGETS.map((t) => t.key).join(', ')}${DRY_RUN ? ' [dry run]' : ''}`);
try { await curseforge(); } catch (error) { console.error(`CurseForge failed: ${error.message}`); process.exit(1); }
