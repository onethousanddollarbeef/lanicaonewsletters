#!/usr/bin/env node
// Rebuilds news-feed.json from the Lani Cao Law Office news feed so the
// homepage "Rapid briefs" section mirrors https://www.lanicao.com/news.

import { readFileSync, writeFileSync } from "node:fs";

const FEED_URL = "https://www.lanicao.com/blog-feed.xml";
const NEWS_PAGE_URL = "https://www.lanicao.com/news";
const OUTPUT_PATH = process.argv[2] || "news-feed.json";
const ITEMS_PER_LANGUAGE = 6;
const SUMMARY_LIMIT_LATIN = 320;
const SUMMARY_LIMIT_CJK = 150;

function decodeEntities(value) {
  return value
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/&#(\d+);/g, (_, code) => String.fromCodePoint(Number(code)))
    .replace(/\s+/g, " ")
    .trim();
}

function tagValue(itemXml, tag) {
  const match = itemXml.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, "i"));
  return match ? decodeEntities(match[1]) : "";
}

// Feed descriptions are the opening of each post, so the excerpt is cut at the
// first sentence boundary that leaves a usable amount of context.
function summarize(text) {
  if (/[\u4e00-\u9fff]/.test(text)) {
    const bounded = text.slice(0, SUMMARY_LIMIT_CJK);

    for (let index = 50; index < bounded.length; index += 1) {
      if ("。！？".includes(bounded[index])) {
        return bounded.slice(0, index + 1).trim();
      }
    }

    return text.length <= SUMMARY_LIMIT_CJK ? text : `${bounded.replace(/[，、；：]$/, "").trim()}…`;
  }

  if (text.length <= SUMMARY_LIMIT_LATIN) {
    return text;
  }

  const bounded = text.slice(0, SUMMARY_LIMIT_LATIN);
  const sentenceEnd = bounded.search(/(?<=\w[.!?])\s/);

  if (sentenceEnd > SUMMARY_LIMIT_LATIN * 0.4) {
    return bounded.slice(0, sentenceEnd).trim();
  }

  const wordBreak = bounded.lastIndexOf(" ");

  return `${bounded.slice(0, wordBreak > 0 ? wordBreak : bounded.length).replace(/[,;:]$/, "").trim()}…`;
}

function parseFeed(xml) {
  const items = [];

  for (const match of xml.matchAll(/<item>([\s\S]*?)<\/item>/g)) {
    const itemXml = match[1];
    const link = tagValue(itemXml, "link");
    const title = tagValue(itemXml, "title");
    const publishedAt = new Date(tagValue(itemXml, "pubDate"));

    if (!link || !title || Number.isNaN(publishedAt.getTime())) {
      continue;
    }

    items.push({
      title,
      summary: summarize(tagValue(itemXml, "description")),
      link,
      date: publishedAt.toISOString().slice(0, 10),
      publishedAt: publishedAt.toISOString(),
      // Some Chinese-language posts are published outside the /zh/ prefix, so the
      // title is the more reliable signal for which language list an item joins.
      isChinese: /\/zh\/post\//.test(link) || /[\u4e00-\u9fff]/.test(title),
    });
  }

  return items.sort((a, b) => b.publishedAt.localeCompare(a.publishedAt));
}

async function loadTraditionalConverter() {
  try {
    const opencc = await import("opencc-js");
    return (opencc.default ?? opencc).Converter({ from: "cn", to: "tw" });
  } catch (error) {
    console.warn("opencc-js unavailable; Traditional Chinese briefs will reuse the Simplified text.");
    return null;
  }
}

function toTraditional(item, convert) {
  if (!convert) {
    return item;
  }

  return {
    ...item,
    title: convert(item.title).replaceAll("特朗普", "川普"),
    summary: convert(item.summary).replaceAll("特朗普", "川普"),
  };
}

function stripInternals({ isChinese, publishedAt, ...item }) {
  return item;
}

async function main() {
  const response = await fetch(FEED_URL, {
    headers: { "user-agent": "lawdaily.us news sync (+https://lawdaily.us)" },
  });

  if (!response.ok) {
    throw new Error(`Feed request failed with status ${response.status}`);
  }

  const items = parseFeed(await response.text());
  const english = items.filter((item) => !item.isChinese).slice(0, ITEMS_PER_LANGUAGE);
  const chinese = items.filter((item) => item.isChinese).slice(0, ITEMS_PER_LANGUAGE);

  if (!english.length && !chinese.length) {
    throw new Error("Feed contained no usable items");
  }

  const convert = await loadTraditionalConverter();
  const feed = {
    source: NEWS_PAGE_URL,
    feed: FEED_URL,
    generatedAt: new Date().toISOString(),
    items: {
      en: english.map(stripInternals),
      zhHans: chinese.map(stripInternals),
      zhHant: chinese.map((item) => stripInternals(toTraditional(item, convert))),
    },
  };

  let previous = null;
  try {
    previous = JSON.parse(readFileSync(OUTPUT_PATH, "utf8"));
  } catch (error) {
    previous = null;
  }

  if (previous && JSON.stringify(previous.items) === JSON.stringify(feed.items)) {
    console.log("No news changes; leaving news-feed.json untouched.");
    return;
  }

  writeFileSync(OUTPUT_PATH, `${JSON.stringify(feed, null, 2)}\n`);
  console.log(`Wrote ${OUTPUT_PATH} with ${feed.items.en.length} English and ${feed.items.zhHans.length} Chinese briefs.`);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
