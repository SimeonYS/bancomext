import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbancomextItem
from itemloaders.processors import TakeFirst
import datetime

pattern = r'(\xa0)?'
base = 'https://www.bancomext.com/sala-de-prensa/comunicados?postyear={}&postmonth='

class BbancomextSpider(scrapy.Spider):
	name = 'bancomext'
	now = datetime.datetime.now()
	year = now.year
	start_urls = [base.format(year)]

	def parse(self, response):
		articles = response.xpath('//div[@class="post-item"]')
		links = []
		for article in articles:
			date = article.xpath('.//time/text()').get()
			date = re.findall(r'\d+\sde\s\w+\sde\s\d+', date)
			post_links = article.xpath('.//h3/a/@href').get()
			links.append(post_links)
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		if self.year > 2012:
			self.year -= 1
			yield response.follow(base.format(self.year), self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h2/text()').get()
		content = response.xpath('//div[@class="post-entry"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BbancomextItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
