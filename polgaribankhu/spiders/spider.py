import scrapy

from scrapy.loader import ItemLoader

from ..items import PolgaribankhuItem
from itemloaders.processors import TakeFirst


class PolgaribankhuSpider(scrapy.Spider):
	name = 'polgaribankhu'
	start_urls = ['https://polgaribank.hu/hirek_aktualitasok']

	def parse(self, response):
		post_links = response.xpath('//div[@class="right"]//div[@class="news"]')
		for post in post_links:
			url = post.xpath('.//a[text()="Tovább"]/@href').get()
			date = post.xpath('.//h2/text()').get()
			if url:
				yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		if post_links:
			next_page = response.xpath('//a[text()="»"]/@href').getall()
			yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		if response.url[-3:] == 'pdf':
			return
		title = response.xpath('//h1[@class="main_title"]/text()').get()
		description = response.xpath('//div[@class="right"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=PolgaribankhuItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
