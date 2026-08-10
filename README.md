# Lanicao Newsletters

A responsive law firm newsletter website with English, Simplified Chinese, and Traditional Chinese content.

## Run locally

```bash
npm install
npm run start
```

## Build

```bash
npm run build
```

## News briefs

The published site (the `gh-pages` branch, served at lawdaily.us) fills its
"Rapid briefs" section from `news-feed.json`, a mirror of the posts on
[lanicao.com/news](https://www.lanicao.com/news). The
`Sync Lani Cao news briefs` workflow rebuilds that file every six hours and
commits it to `gh-pages`; it can also be run on demand from the Actions tab.

To regenerate the file by hand:

```bash
npm install
node scripts/sync-lanicao-news.mjs path/to/news-feed.json
```
