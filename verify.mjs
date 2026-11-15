import { createRequire } from "node:module";
const require = createRequire("D:/project/git-primer/node_modules/");
const { chromium } = require("playwright-core");

const results = [];
const check = (name, cond) => results.push([cond ? "PASS" : "FAIL", name]);
const errors = [];

const browser = await chromium.launch({ channel: "msedge", headless: true });
const page = await browser.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 2 });
page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
page.on("console", (m) => { if (m.type() === "error") errors.push("console.error: " + m.text()); });

await page.goto("http://127.0.0.1:8094/", { waitUntil: "networkidle" });

/* ---------- 结构断言 ---------- */
check("masthead 存在", await page.locator("header.masthead").count() === 1);
check("h1 含『修家谱』", (await page.textContent("h1")).includes("修家谱"));
check("章节=5", await page.locator("section.chapter").count() === 5);
check("小样=4", await page.locator("div.demo").count() === 4);
check("页脚声明 VOL.15", (await page.textContent("footer")).includes("VOL.15"));

/* ---------- DEMO 01 · 七站时间线 ---------- */
await page.locator("#d1").scrollIntoViewIfNeeded();
for (let i = 0; i < 7; i++) await page.click("#g1-next");
check("d1 七站后壳名=OpenClaw", (await page.textContent("#g1-shell")) === "OpenClaw");
check("d1 日志含 2026.11.3", (await page.textContent("#g1-log")).includes("2026.11.3"));
check("d1 下一站已禁用", await page.locator("#g1-next").isDisabled());
await page.click("#g1-reset");
check("d1 重置后壳名=Clawdbot", (await page.textContent("#g1-shell")) === "Clawdbot");

/* ---------- DEMO 02 · 代际分诊器 ---------- */
await page.locator("#d2").scrollIntoViewIfNeeded();
await page.click('.g2-card:has-text("OpenClaw")');
check("d2 OpenClaw 三问一=你自己的设备", (await page.textContent("#g2-a1")).includes("你自己的设备"));
check("d2 判定=第四代", (await page.textContent("#g2-verdict")).includes("第四代"));
await page.click('.g2-card:has-text("ChatGPT")');
check("d2 ChatGPT 判定=第一代", (await page.textContent("#g2-verdict")).includes("第一代"));
await page.click('.g2-card:has-text("Manus")');
check("d2 Manus 判定=第三代", (await page.textContent("#g2-verdict")).includes("第三代"));
await page.click("#g2-reset");
check("d2 重置后复位", (await page.textContent("#g2-verdict")).includes("点一张"));

/* ---------- DEMO 03 · 缝合冲突矩阵 ---------- */
await page.locator("#d3").scrollIntoViewIfNeeded();
await page.click('.g3-chip:has-text("自进化学习闭环")');
await page.click('.g3-chip:has-text("企业级可审计")');
check("d3 自进化×可审计=相斥", (await page.textContent("#g3-verdict")).includes("相斥"));
check("d3 日志含合并即两伤", (await page.textContent("#g3-log")).includes("合并即两伤"));
await page.click("#g3-reset");
await page.click('.g3-chip:has-text("自托管")');
await page.click('.g3-chip:has-text("浏览器专项深度")');
check("d3 自托管×浏览器专项=可共存", (await page.textContent("#g3-verdict")).includes("可共存"));
await page.click("#g3-reset");

/* ---------- DEMO 04 · 版本列车 ---------- */
await page.locator("#d4").scrollIntoViewIfNeeded();
for (let i = 0; i < 6; i++) await page.click("#g4-next");
check("d4 终点=2026.11.3", (await page.textContent("#g4-v")) === "2026.11.3");
check("d4 末站痛点含 31 发循环", (await page.textContent("#g4-p")).includes("31 发循环"));
check("d4 下一站已禁用", await page.locator("#g4-next").isDisabled());
await page.click("#g4-reset");
check("d4 重置后回到 2026.9.9", (await page.textContent("#g4-v")) === "2026.9.9");

/* ---------- 移动端 390px 溢出扫描 ---------- */
await page.setViewportSize({ width: 390, height: 844 });
await page.waitForTimeout(400);
const overflows = await page.$$eval("body *", (els) => {
  const bad = [];
  for (const el of els) {
    if (el.closest(".tbl-wrap")) continue;
    const r = el.getBoundingClientRect();
    if (r.right > 391 && r.width > 0) {
      const tag = el.tagName.toLowerCase();
      if (tag === "svg" || el.querySelector("svg")) continue;
      bad.push(`${tag}.${(el.className || "").toString().slice(0, 30)} right=${Math.round(r.right)}`);
    }
  }
  return bad.slice(0, 12);
});
check("390px 无溢出（" + overflows.length + " 处）", overflows.length === 0);
if (overflows.length) console.log("溢出清单:", JSON.stringify(overflows, null, 1));

/* ---------- 截图目检 ---------- */
await page.setViewportSize({ width: 1200, height: 900 });
await page.evaluate(() => window.scrollTo(0, 0));
await page.waitForTimeout(300);
await page.screenshot({ path: "shot-top.png" });
for (const id of ["d1", "d2", "d3", "d4"]) {
  await page.locator("#" + id).scrollIntoViewIfNeeded();
  await page.waitForTimeout(300);
  await page.locator("#" + id).screenshot({ path: `shot-${id}.png` });
}

console.log("=== 结果 ===");
let pass = 0;
for (const [s, n] of results) { console.log(s, n); if (s === "PASS") pass++; }
console.log(`${pass}/${results.length} PASS`);
console.log("JS 错误:", errors.length === 0 ? "none" : errors.join(" | "));
await browser.close();
process.exit(pass === results.length && errors.length === 0 ? 0 : 1);
