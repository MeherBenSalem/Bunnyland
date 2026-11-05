// Renders the listing artwork in marketing/images/ from real in-game screenshots, the mod's own item textures and
// logo, and the bundled OFL fonts. Usage (from the repository root):
//   NODE_PATH="$(npm root -g)" node marketing/source/render.cjs [name...]
// Requires the `playwright` package with a Chromium build available.
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

// The release and the supported Minecraft versions. Adding a version is one line here
// (plus one row in the compatibility table of curseforge/description.md).
const RELEASE = { version: '1.0', name: 'First Bloom' };
const VERSIONS = [
  { minecraft: '1.20.1', loaders: ['Forge', 'Fabric'] },
  { minecraft: '1.21.1', loaders: ['NeoForge', 'Fabric'] },
  { minecraft: '26.2', loaders: ['NeoForge', 'Fabric'] },
  { minecraft: '26.3', loaders: ['NeoForge', 'Fabric'] },
];
const LOADERS = ['Fabric', 'Forge', 'NeoForge'].filter((loader) => VERSIONS.some((v) => v.loaders.includes(loader)));

const root = path.resolve(__dirname, '..', '..');
const out = path.join(root, 'marketing', 'images');
const shots = path.join(out, 'screenshots');
const fonts = path.join(__dirname, 'fonts');
const textures = path.join(root, 'src', 'main', 'resources', 'assets', 'bunnyland', 'textures');
const url = (file) => 'file://' + file;
const shot = (name) => url(path.join(shots, name));
const source = (name) => url(path.join(__dirname, name));
const texture = (name) => url(path.join(textures, name));

// Names and order match creature/Species.java and the en_us lang file.
const CREATURES = [
  ['cotton_bunny', 'Cotton Bunny'], ['strawberry_bunny', 'Strawberry Bunny'], ['moon_bunny', 'Moon Bunny'],
  ['lavender_bunny', 'Lavender Bunny'], ['snowball_bunny', 'Snowball Bunny'], ['blossom_fox', 'Blossom Fox'],
  ['cloud_kitty', 'Cloud Kitty'], ['strawberry_mouse', 'Strawberry Mouse'], ['honey_bear', 'Honey Bear'],
  ['moon_deer', 'Moon Deer'], ['pastel_axolotl', 'Pastel Axolotl'], ['tiny_swan', 'Tiny Swan'],
  ['rainbow_butterfly', 'Rainbow Butterfly'], ['cherry_blossom_bird', 'Cherry Blossom Bird'], ['dreamy_hamster', 'Dreamy Hamster'],
];
const NIGHT = new Set(['moon_bunny', 'blossom_fox', 'moon_deer', 'dreamy_hamster']);
const TREATS = [['bunny_biscuit', 'Bunny Biscuit'], ['strawberry_tart', 'Strawberry Tart'], ['moon_cookie', 'Moon Cookie'],
  ['blossom_mochi', 'Blossom Mochi'], ['fish_cracker', 'Fish Cracker'], ['honey_cake', 'Honey Cake'],
  ['seed_medley', 'Seed Medley'], ['flower_nectar', 'Flower Nectar']];
// Collar and bow textures are greyscale and tinted in game (item/DyeableCosmeticItem.java defaults).
const COSMETICS = [['pet_collar', 'Pet Collar', '#f7a8c8', 'pet_collar_bell'], ['pet_bow', 'Pet Bow', '#ff8fb8'],
  ['flower_crown', 'Flower Crown'], ['tiny_top_hat', 'Tiny Top Hat'], ['party_hat', 'Party Hat'], ['star_clip', 'Star Clip'],
  ['heart_glasses', 'Heart Glasses'], ['cozy_scarf', 'Cozy Scarf']];
const TOYS = [['yarn_ball', 'Yarn Ball'], ['squeaky_carrot', 'Squeaky Carrot'], ['feather_wand', 'Feather Wand']];
// Moods from creature/Mood.java.
const MOODS = [['a little lonely', 'under 25', '#9db7e0'], ['content', '25+', '#c6a6e8'], ['happy', '60+', '#f59cbc'],
  ['overjoyed', '85+', '#ef5f92']];

const css = `
@font-face { font-family: BlDisplay; src: url('${url(path.join(fonts, 'fredoka.ttf'))}'); }
@font-face { font-family: BlText; src: url('${url(path.join(fonts, 'nunito.ttf'))}'); font-weight: 400; }
@font-face { font-family: BlText; src: url('${url(path.join(fonts, 'nunito-extrabold.ttf'))}'); font-weight: 800; }
:root { --text:#5b3d5f; --dim:#94789a; --plum:#4a2c50; --pink:#f59cbc; --pink-deep:#e2648f; --lav:#b7a2ee; --lav-deep:#8f74d8;
        --mint:#93dcc2; --sky:#9cc8f5; --gold:#f3c45e; --cream:#fff8f4; --line:rgba(226,100,143,.28); }
* { box-sizing: border-box; }
html, body { margin: 0; background: var(--cream); color: var(--text); font-family: BlText, sans-serif; }
.stage { position: relative; overflow: hidden; background: linear-gradient(160deg, #fff3f6 0%, #fbeefb 50%, #f1ecff 100%); }
.display { font-family: BlDisplay, sans-serif; }
.candy { background: linear-gradient(100deg, #ef6f9c 0%, #f08bb4 35%, #b48ef0 75%, #8f74d8 100%);
         -webkit-background-clip: text; background-clip: text; color: transparent; }
.soft { filter: drop-shadow(0 3px 0 rgba(255,255,255,.95)) drop-shadow(0 10px 24px rgba(226,100,143,.25)); }
.kicker { font-family: BlDisplay, sans-serif; color: var(--pink-deep); letter-spacing: .14em; font-size: 24px; text-transform: uppercase; }
.heart { display: inline-block; width: 22px; height: 20px; margin: 0 12px 0 0; vertical-align: -2px;
         background: var(--pink-deep); -webkit-mask: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 22 20'><path d='M11 19.5 1.8 10.6C-.6 8.2-.6 4.3 1.8 2c2.3-2.3 6-2.3 8.3 0L11 2.9l.9-.9c2.3-2.3 6-2.3 8.3 0 2.4 2.3 2.4 6.2 0 8.6Z'/></svg>") center / contain no-repeat;
         mask: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 22 20'><path d='M11 19.5 1.8 10.6C-.6 8.2-.6 4.3 1.8 2c2.3-2.3 6-2.3 8.3 0L11 2.9l.9-.9c2.3-2.3 6-2.3 8.3 0 2.4 2.3 2.4 6.2 0 8.6Z'/></svg>") center / contain no-repeat; }
.rule { height: 4px; border-radius: 2px; background: radial-gradient(circle, var(--pink) 0 2px, transparent 2.5px) 0 0 / 14px 4px repeat-x; }
.frame { position: relative; border: 7px solid #fff; border-radius: 22px; overflow: hidden; background: #fff;
         box-shadow: 0 0 0 2px rgba(226,100,143,.35), 0 26px 60px rgba(120,60,120,.28), 0 6px 14px rgba(120,60,120,.12); }
.frame > img { display: block; width: 100%; }
canvas.motes { position: absolute; left: 0; top: 0; width: 100%; height: 100%; pointer-events: none; }
.wash { position: absolute; inset: 0; background: radial-gradient(ellipse at 70% 45%, rgba(255,255,255,0) 30%, rgba(255,240,246,.55) 100%); }
.backdrop { position: absolute; inset: -40px; background-size: cover; background-position: center; filter: blur(18px) brightness(1.18) saturate(1.05); }
.pill { display: inline-block; border-radius: 999px; padding: 9px 22px 7px; margin-right: 12px; font-family: BlDisplay, sans-serif; font-size: 22px;
        color: #fff; background: linear-gradient(100deg, #ef7ba5, #b394ef); box-shadow: 0 6px 16px rgba(180,90,150,.3); }
.pill.ghost { color: var(--pink-deep); background: rgba(255,255,255,.85); box-shadow: 0 0 0 2px rgba(226,100,143,.5), 0 6px 16px rgba(180,90,150,.15); }
.label { position: absolute; font-family: BlDisplay, sans-serif; font-size: 23px; color: var(--plum); background: rgba(255,255,255,.95);
         border-radius: 999px; padding: 8px 20px 6px; white-space: nowrap; box-shadow: 0 0 0 2px rgba(226,100,143,.55), 0 10px 26px rgba(120,60,120,.3); z-index: 2; }
.label small { font-family: BlText, sans-serif; font-size: 18px; color: var(--dim); margin-left: 8px; }
ul.points { list-style: none; padding: 0; margin: 0; }
ul.points li { position: relative; padding-left: 38px; margin: 0 0 16px; font-size: 27px; line-height: 1.3; color: var(--text); }
ul.points li::before { content: ''; position: absolute; left: 0; top: 8px; width: 22px; height: 20px; background: var(--pink);
  -webkit-mask: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 22 20'><path d='M11 19.5 1.8 10.6C-.6 8.2-.6 4.3 1.8 2c2.3-2.3 6-2.3 8.3 0L11 2.9l.9-.9c2.3-2.3 6-2.3 8.3 0 2.4 2.3 2.4 6.2 0 8.6Z'/></svg>") center / contain no-repeat;
  mask: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 22 20'><path d='M11 19.5 1.8 10.6C-.6 8.2-.6 4.3 1.8 2c2.3-2.3 6-2.3 8.3 0L11 2.9l.9-.9c2.3-2.3 6-2.3 8.3 0 2.4 2.3 2.4 6.2 0 8.6Z'/></svg>") center / contain no-repeat; }
ul.points li:nth-child(3n+2)::before { background: var(--lav); }
ul.points li:nth-child(3n)::before { background: var(--mint); }
b.hi { color: var(--plum); font-weight: 800; }
.stats { display: flex; gap: 14px; margin-top: 22px; }
.stats > div { flex: 1; padding: 14px 20px 12px; border-radius: 18px; background: rgba(255,255,255,.92);
               box-shadow: 0 0 0 2px rgba(226,100,143,.25), 0 14px 34px rgba(120,60,120,.18); text-align: center; }
.stats .t { font-family: BlText, sans-serif; font-weight: 800; font-size: 16px; letter-spacing: .1em; text-transform: uppercase; color: var(--dim); }
.stats .v { font-family: BlDisplay, sans-serif; font-size: 34px; color: var(--plum); margin-top: 2px; white-space: nowrap; }
.items { display: flex; gap: 12px; margin-top: 22px; }
.items > div { flex: 1; border-radius: 18px; background: rgba(255,255,255,.92); padding: 12px 6px 10px; text-align: center;
               box-shadow: 0 0 0 2px rgba(226,100,143,.25), 0 14px 34px rgba(120,60,120,.18); }
.items canvas, .items img { display: block; margin: 0 auto; image-rendering: pixelated; }
.items .n { font-family: BlDisplay, sans-serif; font-size: 17px; line-height: 1.1; color: var(--plum); margin-top: 6px; }
pre.code { margin: 0; font-family: 'DejaVu Sans Mono', monospace; font-size: 22px; line-height: 1.5; color: var(--text); }
`;

// Drifting cherry petals and golden sparkles, the pastel counterpart of the sibling kits' motes.
// Deterministic so renders are reproducible.
const motes = (count = 46, seed = 7) => `<canvas class="motes"></canvas><script>
(() => { const c = document.currentScript.previousElementSibling; const r = c.getBoundingClientRect();
  c.width = r.width; c.height = r.height; const g = c.getContext('2d'); let s = ${seed};
  const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const sparkle = (x, y, z, a) => { g.save(); g.translate(x, y); g.fillStyle = 'rgba(255,214,110,' + a + ')';
    g.beginPath(); g.moveTo(0, -z * 3); g.quadraticCurveTo(0, 0, z * 3, 0); g.quadraticCurveTo(0, 0, 0, z * 3);
    g.quadraticCurveTo(0, 0, -z * 3, 0); g.quadraticCurveTo(0, 0, 0, -z * 3); g.fill(); g.restore(); };
  const petal = (x, y, z, a, rot, pink) => { g.save(); g.translate(x, y); g.rotate(rot);
    const h = g.createLinearGradient(-z * 4, 0, z * 4, 0); h.addColorStop(0, 'rgba(' + pink + ',' + a + ')'); h.addColorStop(1, 'rgba(255,240,246,' + a + ')');
    g.fillStyle = h; g.beginPath(); g.ellipse(0, 0, z * 4.2, z * 2.4, 0, 0, Math.PI * 2); g.fill(); g.restore(); };
  for (let i = 0; i < ${count}; i++) { const x = rnd() * c.width, y = rnd() * c.height, a = .45 + rnd() * .45, z = 1.4 + rnd() * 2.2;
    if (rnd() < .32) sparkle(x, y, z, a); else petal(x, y, z, a, rnd() * Math.PI, rnd() < .5 ? '246,150,186' : '250,184,210'); } })();
</script>`;

// Item textures (16x16), drawn pixel-sharp; greyscale ones are tinted the way Minecraft tints dyeable items.
const itemScript = `<script>
(() => { const cells = [...document.querySelectorAll('canvas.item')]; let left = cells.length;
  const done = () => { if (--left <= 0) document.body.dataset.items = 'ready'; };
  if (!left) document.body.dataset.items = 'ready';
  for (const c of cells) { const size = +c.dataset.s; c.width = c.height = size; const g = c.getContext('2d'); g.imageSmoothingEnabled = false;
    const base = new Image(); base.src = c.dataset.src;
    base.onload = () => { g.drawImage(base, 0, 0, size, size);
      if (c.dataset.tint) { g.globalCompositeOperation = 'multiply'; g.fillStyle = c.dataset.tint; g.fillRect(0, 0, size, size);
        g.globalCompositeOperation = 'destination-in'; g.drawImage(base, 0, 0, size, size); g.globalCompositeOperation = 'source-over'; }
      if (c.dataset.over) { const over = new Image(); over.src = c.dataset.over; over.onload = () => { g.drawImage(over, 0, 0, size, size); done(); }; }
      else done(); }; } })();
</script>`;
const item = (name, size = 64, tint = '', over = '') => `<canvas class="item" data-src="${texture(`item/${name}.png`)}" data-s="${size}"${tint ? ` data-tint="${tint}"` : ''}${over ? ` data-over="${texture(`item/${over}.png`)}"` : ''} style="width:${size}px;height:${size}px"></canvas>`;
const itemRow = (list, size = 56) => `<div class="items">${list.map(([name, title, tint, over]) => `<div>${item(name, size, tint, over)}<div class="n">${title}</div></div>`).join('')}</div>`;

const page = (width, height, body, transparent = false) => `<!doctype html><html><head><meta charset="utf-8"><style>${css}
body { width: ${width}px; height: ${height}px; } .stage { width: ${width}px; height: ${height}px; }
${transparent ? 'html, body, .stage { background: transparent; }' : ''}</style></head>
<body><div class="stage">${body}</div>${itemScript}</body></html>`;

const heartSvg = (fill, size) => `<svg width="${size}" height="${Math.round(size * 20 / 22)}" viewBox="0 0 22 20" style="display:block"><path fill="${fill}" stroke="#fff" stroke-width="1.6" d="M11 19.5 1.8 10.6C-.6 8.2-.6 4.3 1.8 2c2.3-2.3 6-2.3 8.3 0L11 2.9l.9-.9c2.3-2.3 6-2.3 8.3 0 2.4 2.3 2.4 6.2 0 8.6Z"/></svg>`;

// A section heading: a candy ribbon with the title, readable on CurseForge's light and dark themes.
const header = (title) => page(1400, 120, `
  <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:22px">
    <div class="rule" style="width:240px;opacity:.9;-webkit-mask-image:linear-gradient(90deg,transparent,#000);mask-image:linear-gradient(90deg,transparent,#000)"></div>
    ${heartSvg('#b7a2ee', 30)}
    <div style="position:relative;padding:14px 54px 12px;border-radius:999px;background:linear-gradient(100deg,#f592b7 0%,#f3a6c6 45%,#c3adf3 100%);
                box-shadow:0 0 0 4px #fff,0 0 0 6px rgba(226,100,143,.45),0 12px 28px rgba(120,60,120,.3)">
      <div class="display" style="font-size:46px;line-height:1;color:#fff;white-space:nowrap;text-shadow:0 3px 0 rgba(190,80,130,.45)">${title}</div></div>
    ${heartSvg('#f59cbc', 30)}
    <div class="rule" style="width:240px;opacity:.9;-webkit-mask-image:linear-gradient(90deg,#000,transparent);mask-image:linear-gradient(90deg,#000,transparent)"></div>
  </div>`, true);

// A feature card: copy on the left, artwork on the right. Bullets never end on a one-word line.
const card = ({ kicker, title, points, art, width = 1600, height = 900, artWidth = 980 }) => page(width, height, `
  <div class="backdrop" style="background-image:url('${source('backdrop.jpg')}');opacity:.5"></div>
  <div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(255,247,250,.93) 0%,rgba(255,247,250,.86) 34%,rgba(250,240,255,.55) 62%,rgba(245,240,255,.35) 100%)"></div>
  <div class="wash"></div>${motes()}
  <div style="position:absolute;left:76px;top:0;bottom:0;width:${width - artWidth - 176}px;display:flex;flex-direction:column;justify-content:center">
    <div class="kicker"${kicker.length > 22 ? ' style="font-size:20px;letter-spacing:.1em"' : ''}><span class="heart"></span>${kicker}</div>
    <div class="display candy soft" style="font-size:66px;line-height:1.02;margin:16px 0 22px">${title}</div>
    <div class="rule" style="width:70%;margin-bottom:30px"></div>
    <ul class="points">${points.map((point) => `<li>${point.replace(/ (\S+)$/, '&nbsp;$1')}</li>`).join('')}</ul>
  </div>
  <div style="position:absolute;right:56px;top:50%;transform:translateY(-50%);width:${artWidth}px">${art}</div>`);

// An exact region (x, y, w, h in source pixels, 1920x1080 by default) of a capture, scaled to W pixels wide.
const region = (file, x, y, w, h, W, full = 1920) => `<div style="position:relative;width:${W}px;height:${Math.round(W * h / w)}px;overflow:hidden">
    <img src="${shot(file)}" style="position:absolute;max-width:none;width:${W * full / w}px;left:${-x * W / w}px;top:${-y * W / w}px"></div>`;
const framed = (inner, style = '') => `<div class="frame" style="${style}">${inner}</div>`;
const label = (text, style, small = '') => `<div class="label" style="${style}">${text}${small ? `<small>${small}</small>` : ''}</div>`;
const stats = (items) => `<div class="stats">${items.map(([t, v, flex]) =>
  `<div${flex ? ` style="flex:${flex}"` : ''}><div class="v">${v}</div><div class="t">${t}</div></div>`).join('')}</div>`;
// Two overlapping captures, the first top left and the second bottom right.
const pair = (first, second, firstLabel, secondLabel, height = 640, width = '73%') => `<div style="position:relative;height:${height}px">
    <div class="frame" style="position:absolute;left:0;top:0;width:${width}">${first}</div>
    <div class="frame" style="position:absolute;right:0;bottom:0;width:${width}">${second}</div>
    ${label(firstLabel, 'left:24px;top:22px')}${label(secondLabel, 'right:24px;bottom:22px')}</div>`;
// Two captures side by side, each with a label in its top left corner.
const duo = (first, second, firstLabel, secondLabel) => `<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px">
    <div style="position:relative">${framed(first)}${label(firstLabel, 'left:20px;top:18px')}</div>
    <div style="position:relative">${framed(second)}${label(secondLabel, 'left:20px;top:18px')}</div></div>`;
const img = (file) => `<img src="${shot(file)}" style="display:block;width:100%">`;
const code = (file, body) => `<div class="frame" style="background:rgba(255,255,255,.96);padding:24px 34px">
  <div style="font-family:BlText;font-weight:800;font-size:18px;letter-spacing:.08em;color:var(--dim);margin-bottom:10px">${file}</div><pre class="code">${body}</pre></div>`;
const k = (t) => `<span style="color:#d0578a">${t}</span>`;
const v = (t) => `<span style="color:#7a5bd0">${t}</span>`;
const cm = (t) => `<span style="color:#b49bb8">${t}</span>`;

const versionText = VERSIONS.map((ver) => ver.minecraft).join(' · ');

const assets = {
  banner: () => page(1800, 600, `
    <img src="${shot('cherry-grove.jpg')}" style="position:absolute;right:-70px;top:-118px;width:1300px;-webkit-mask-image:linear-gradient(90deg,transparent 0%,#000 30%);mask-image:linear-gradient(90deg,transparent 0%,#000 30%)">
    <div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(255,246,250,.98) 0%,rgba(255,246,250,.94) 30%,rgba(255,246,250,.4) 52%,rgba(255,246,250,0) 70%)"></div>
    <div style="position:absolute;inset:0;background:linear-gradient(0deg,rgba(255,240,247,.55) 0%,rgba(255,240,247,0) 26%)"></div>
    ${motes(48, 11)}
    <div style="position:absolute;left:86px;top:62px;width:960px">
      <div class="kicker"><span class="heart"></span>${RELEASE.version} · ${RELEASE.name}</div>
      <div style="display:flex;align-items:center;gap:26px;margin:14px 0 6px">
        <img src="${source('logo.png')}" style="width:150px;height:150px;image-rendering:pixelated;filter:drop-shadow(0 12px 24px rgba(200,90,150,.35))">
        <div class="display candy soft" style="font-size:132px;line-height:1;white-space:nowrap">Bunnyland</div></div>
      <div class="rule" style="width:620px;margin:16px 0 24px"></div>
      <div style="font-family:BlDisplay;font-size:40px;color:var(--plum);line-height:1.2">A world full of cute animals.</div>
      <div style="font-size:27px;color:var(--text);line-height:1.35;margin-top:8px">Discover, befriend, dress up and care for<br>fifteen fairytale creatures.</div>
      <div style="margin-top:30px">${LOADERS.map((l) => `<span class="pill">${l}</span>`).join('')}<span class="pill ghost">GeckoLib</span></div>
      <div style="margin-top:16px;font-family:BlDisplay;font-size:26px;color:var(--dim)">Minecraft ${versionText}</div>
    </div>`),

  icon: () => page(512, 512, `
    <div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 40%,#fff6fa 0%,#fbe0ee 55%,#e6dcff 100%)"></div>${motes(26, 5)}
    <div style="position:absolute;left:52px;top:52px;width:408px;height:408px;border-radius:50%;background:#fff;
                box-shadow:0 0 0 6px #fff,0 0 0 10px #f59cbc,0 0 0 14px #fff,0 0 0 17px #c3adf3,0 24px 50px rgba(160,80,140,.35)"></div>
    <img src="${source('logo.png')}" style="position:absolute;left:64px;top:64px;width:384px;height:384px;image-rendering:pixelated">
    ${[[256, 30], [482, 256], [256, 482], [30, 256]].map(([x, y], i) => `<div style="position:absolute;left:${x - 17}px;top:${y - 15}px">${heartSvg(i % 2 ? '#b7a2ee' : '#f59cbc', 34)}</div>`).join('')}`),

  'card-creatures': () => card({
    kicker: 'Fifteen creatures', title: 'Fairytale<br>friends',
    points: ['Five kinds of bunny, a fox, a kitty, a mouse and a bear', 'A deer, an axolotl, a swan, a butterfly, a bird and a hamster',
      'Each with its own 3D model and animations', 'Blinking faces and original sounds', 'Moon icons mark the night creatures'],
    art: `<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:14px">${CREATURES.map(([id, name]) => `
      <div style="position:relative;border-radius:18px;background:#fff;padding:6px 6px 0;box-shadow:0 0 0 2px rgba(226,100,143,.3),0 14px 30px rgba(120,60,120,.22)">
        <div style="position:relative;aspect-ratio:1;overflow:hidden;border-radius:13px">
          <img src="${shot(`portraits/${id}.jpg`)}" style="position:absolute;width:132%;left:-16%;top:-14%;max-width:none"></div>
        <div class="display" style="font-size:${name.length > 16 ? 15 : 18}px;color:var(--plum);text-align:center;padding:7px 2px 7px;white-space:nowrap">${name}</div>
        ${NIGHT.has(id) ? `<div style="position:absolute;right:12px;top:12px;width:34px;height:34px;border-radius:50%;background:rgba(74,44,80,.85);display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 2px #fff">${item('moon_cookie', 24)}</div>` : ''}
      </div>`).join('')}</div>` }),

  'card-habitats': () => card({
    kicker: 'Out in the wild', title: 'Find them<br>all over',
    points: ['Meadows, flower forests, plains and cherry groves', 'Snowy plains, taigas, groves and slopes', 'Forests, birch woods, rivers and swamps',
      'Sneak up on the shy ones, or they run', 'Day creatures sleep at night, night creatures nap by day'],
    art: `<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px">${[['cherry-grove.jpg', 'Cherry grove'], ['snowy-taiga.jpg', 'Snowy taiga'],
      ['river.jpg', 'River'], ['forest.jpg', 'Forest']].map(([file, name]) => `<div style="position:relative">${framed(region(file, 0, 60, 1920, 1020, 467))}
      ${label(name, 'left:18px;bottom:16px;font-size:21px')}</div>`).join('')}</div>` }),

  'card-night': () => card({
    kicker: 'After dark', title: 'Night<br>creatures',
    points: ['Moon Bunny, Blossom Fox, Moon Deer and Dreamy Hamster', 'Awake at night, napping through the day',
      'Glowing markings, starry spots and a floating crescent moon', 'Moon Bunnies jump high and never take fall damage',
      'Rare variants sparkle, and most of them glow'],
    art: framed(region('moonlit-night.jpg', 160, 140, 1600, 900, 978)) +
      stats([['Night creatures', '4'], ['Moon Bunnies', 'no fall damage'], ['Rare variants', 'glow', 1]]) }),

  'card-befriend': () => card({
    kicker: 'Treats & trust', title: 'Make a<br>friend',
    points: ['Craft each creature’s favourite treat', 'Hold it out and wild ones come closer', 'Hearts mean yes, smoke means try again',
      'Sneak and pet them to see how they feel', 'Sit, follow, name, leash and carry your pets'],
    art: duo(region('befriend.jpg', 560, 150, 800, 780, 466), region('petting.jpg', 560, 150, 800, 780, 466),
      'A treat', 'A pat') + itemRow(TREATS, 48) }),

  'card-variants': () => card({
    kicker: '73 colourways', title: 'Rare and<br>wonderful',
    points: ['Three to five colourways for every creature', 'Twenty-five rare variants, born only by breeding',
      'An 8% chance per baby, doubled for overjoyed parents', 'Rare creatures sparkle and most glow in the dark'],
    art: pair(region('variants-cotton-bunny.jpg', 120, 135, 1680, 945, 715), region('rare-variants.jpg', 120, 135, 1680, 945, 715),
      'Cotton Bunny colours', '★ Rare variants', 590) +
      stats([['Variants', '73'], ['Rare', '25'], ['Rare baby chance', '8%', 1.4], ['Overjoyed parents', '×2', 1.4]]) }),

  'card-dress-up': () => card({
    kicker: 'Dress-up', title: 'Dress them<br>up',
    points: ['Six accessories, fitted to every creature', 'Collars with a gold bell, and bows, dyed any colour',
      'One accessory plus a collar and a bow at once', 'Shears take them off again, one at a time'],
    art: framed(region('dress-up.jpg', 140, 160, 1640, 820, 978)) + itemRow(COSMETICS, 52) }),

  'card-care': () => card({
    kicker: 'Pet care', title: 'Cosy and<br>cared for',
    points: ['Happiness rises with petting, treats, toys and naps', 'Happy pets slowly heal; overjoyed ones get the zoomies',
      'Fill a Feeding Bowl and pets eat by themselves', 'Pets curl up in their beds at bedtime', 'No pet ever dies or runs away from neglect'],
    art: framed(region('beds-and-bowls.jpg', 180, 220, 1560, 780, 978)) + `<div class="stats">${MOODS.map(([name, at, color]) => `
      <div><div style="display:flex;justify-content:center;margin-bottom:4px">${heartSvg(color, 34)}</div>
        <div class="display" style="font-size:25px;color:var(--plum);white-space:nowrap">${name}</div><div class="t">${at}</div></div>`).join('')}</div>` }),

  'card-personality': () => card({
    kicker: 'Personalities', title: 'Every one<br>is different',
    points: ['Cotton Bunnies shed fluff for beds, string and wool', 'Honey Bears lick beehives, bunnies nibble berries',
      'Cloud Kitties leave a gift when you wake up', 'Butterflies plant flowers, birds dance to jukeboxes', 'Cygnets paddle after their parents'],
    art: pair(region('forest.jpg', 120, 100, 1680, 945, 715), region('river.jpg', 120, 135, 1680, 945, 715), 'Forest friends', 'A swan family', 700, '66%') }),

  'card-journal': () => card({
    kicker: 'Pet Journal', title: 'Collect them<br>all',
    points: ['Every creature you see is written down', 'Discovered, befriended and rare variants, counted',
      'A live model you can turn on every page', 'Habitat, treat, favourite foods and a tip', 'Silhouettes and hints for the ones still out there'],
    art: pair(region('journal-index.jpg', 500, 250, 920, 580, 715), region('journal-honey-bear.jpg', 500, 250, 920, 580, 715),
      'Index', 'Honey Bear', 760, '66%') }),

  'card-config': () => card({
    kicker: 'Make it yours', title: 'Tune every<br>number',
    points: ['Spawn weight and group size per creature', 'Rare odds, breeding happiness and care decay',
      'Turn off shyness, hive licking or berry nibbling', 'Spawn biomes are data-pack biome tags'],
    art: `<div style="display:flex;flex-direction:column;gap:24px">
      ${code('config/bunnyland-common.toml', `${k('[spawning.cotton_bunny]')}
  ${k('weight')} = ${v('8')}       ${cm('# vanilla sheep use 12')}
  ${k('minGroup')} = ${v('2')}
  ${k('maxGroup')} = ${v('4')}
${k('[breeding]')}
  ${k('rareOffspringChance')} = ${v('0.08')}
  ${k('breedingHappiness')} = ${v('40')}
${k('[behaviour]')}
  ${k('wildCreaturesAreShy')} = ${v('true')}`)}
      ${code('data/bunnyland/tags/worldgen/biome/spawns/tiny_swan.json', `{ ${k('"replace"')}: ${v('false')},
  ${k('"values"')}: [ ${v('"minecraft:river"')}, ${v('"minecraft:swamp"')} ] }`)}</div>` }),
};

const headers = { 'header-creatures': 'The Creatures', 'header-habitats': 'Where to Find Them', 'header-befriend': 'Befriending',
  'header-variants': 'Variants & Breeding', 'header-dress-up': 'Dress Up', 'header-care': 'Pet Care', 'header-personality': 'Personalities',
  'header-journal': 'The Pet Journal', 'header-recipes': 'Recipes', 'header-config': 'Configuration', 'header-everything': 'Everything Else',
  'header-compatibility': 'Downloads & Compatibility', 'header-faq': 'Questions', 'header-gallery': 'Gallery' };
for (const [name, title] of Object.entries(headers)) assets[name] = () => header(title);
assets.divider = () => page(1400, 40, `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:14px">
  <div class="rule" style="width:480px;-webkit-mask-image:linear-gradient(90deg,transparent,#000);mask-image:linear-gradient(90deg,transparent,#000)"></div>
  ${heartSvg('#b7a2ee', 20)}${heartSvg('#f59cbc', 26)}${heartSvg('#93dcc2', 20)}
  <div class="rule" style="width:480px;-webkit-mask-image:linear-gradient(90deg,#000,transparent);mask-image:linear-gradient(90deg,#000,transparent)"></div></div>`, true);

(async () => {
  const wanted = process.argv.slice(2);
  const browser = await chromium.launch();
  fs.mkdirSync(out, { recursive: true });
  for (const [name, build] of Object.entries(assets)) {
    if (wanted.length && !wanted.includes(name)) continue;
    const html = build();
    const size = html.match(/body \{ width: (\d+)px; height: (\d+)px; \}/);
    const tab = await browser.newPage({ viewport: { width: +size[1], height: +size[2] }, deviceScaleFactor: 1 });
    const file = path.join(__dirname, `.render-${name}.html`);
    fs.writeFileSync(file, html);
    await tab.goto(url(file));
    await tab.evaluate(() => document.fonts.ready);
    await tab.waitForLoadState('networkidle');
    await tab.waitForFunction(() => document.body.dataset.items === 'ready');
    await tab.screenshot({ path: path.join(out, `${name}.png`), omitBackground: name === 'divider' || name.startsWith('header-') });
    fs.unlinkSync(file);
    await tab.close();
    console.log('rendered', name);
  }
  await browser.close();
})().catch((error) => { console.error(error); process.exit(1); });
