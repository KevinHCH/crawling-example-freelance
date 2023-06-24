import { chromium } from "playwright-chromium"
import { URL } from "url"
import { writeFileSync } from "node:fs"
const urls = [
  "https://www.startups.fyi/product",
  "https://www.startups.fyi/product?e52a550f_page=2",
  "https://www.startups.fyi/product?e52a550f_page=3",
]
// =================================================
// * selector
// =================================================
const startupsSelector = ".interview-card"
const startupNameSelector = ".name-title"
const startupRevenueSelector = ".person-designation-flex-div div:last-child"
const startupDescriptionSelector = ".card-para"
const startupLinkSelector = ".pirsch-event-webclick"
const browser = await chromium.launch()
const page = await browser.newPage()
const startupsData = []
for (const url of urls) {
  await page.goto(url, { waitUntil: "networkidle" })
  const starttupLinks = await page.$$eval(startupsSelector, (elements) =>
    elements.map((el) => el.href)
  )
  console.log("startups on this link:", starttupLinks.length)
  let i = 0
  for (const link of starttupLinks) {
    await page.goto(link, { waitUntil: "networkidle" })
    console.log("link:", link, " - ", i, "of", starttupLinks.length)
    i++
    const startupName = await page.$eval(startupNameSelector, (el) =>
      el.innerText.trim()
    )
    const startupDescription = await page.$eval(
      startupDescriptionSelector,
      (el) => el.innerText.trim()
    )
    const startupRevenue = await page.$eval(startupRevenueSelector, (el) =>
      el.innerText.trim()
    )
    const startupLink = await page.$eval(startupLinkSelector, (el) => el.href)
    const { origin } = new URL(startupLink)
    console.log("startupName:", startupName)
    const data = await page.evaluate(() => {
      function kebabCase(str) {
        return str.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase()
      }
      const div = document.querySelector(
        "#w-node-ff2e0bc1-92d9-b6ad-ddce-4fa56601f5e8-a330d4fe"
      )
      const values = {}
      const divBlocks = div.getElementsByClassName("div-block-58")
      for (let i = 0; i < divBlocks.length; i++) {
        const key = divBlocks[i]
          .querySelector(".project-tag")
          .textContent.replace(/🗓|👥|🌍|💰|🤑|⏰|👻|💪/g, "")
          .trim()
        const value = divBlocks[i]
          .querySelector("div:last-child")
          .textContent.trim()
        values[kebabCase(key)] = value
      }
      function camelize(str) {
        return str.replace(/[-_](.)/g, (_, char) => char.toUpperCase())
      }

      function kebabCase(str) {
        return str.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase()
      }
      return values
    })
    startupsData.push({
      name: startupName,
      description: startupDescription,
      revenue: startupRevenue,
      url: origin,
      data: data,
    })
  } //starttupLinks
} //for urls
writeFileSync("startups.json", JSON.stringify(startupsData, null, 2))
await page.close()
await browser.close()
