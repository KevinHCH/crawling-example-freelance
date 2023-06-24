import asyncio, httpx
from rich import print
async def async_req(client, url):
  response = await client.get(url)
  return response.json()

async def main(urls):
  
  async with httpx.AsyncClient() as client:
    tasks = []
    for url in urls:
      tasks.append(async_req(client, url))

    data = await asyncio.gather(*tasks)
  return data

urls = [
  'https://api.ipify.org?format=json',
  'https://api.ipify.org?format=json',
  'https://api.ipify.org?format=json',
  'https://api.ipify.org?format=json'
]
results = asyncio.run(main(urls))
errors = sum([1 for e in results if 'Error' in e.values()])
sucesses = sum([1 for e in results if 'Successful' in e.values()])
output = {"sucesses": sucesses, "errors": errors}
print(output)
print(results)