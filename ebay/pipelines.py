# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request


class EbayPipeline(object):
    def process_item(self, item, spider):
        return item


class MyImagesPipeline(ImagesPipeline):
    # def item_completed(self, results, item, info):
        # image_paths = [x['path'] for ok, x in results if ok]
        # if not image_paths:
        #     raise DropItem("Item contains no images")
        # item['image_paths'] = image_paths
        # return item

    def file_path(self, request, response=None, info=None):
        return request.meta.get('image_path', '')

    def get_media_requests(self, item, info):
        for i, image_url in enumerate(item['image_urls']):
            yield Request(image_url, meta={'image_path': ''.join([item['image_path'], '/', str(i), '.jpg'])})
        # img_url = item['img_url']
        # meta = {'filename': item['name']}
        # yield Request(url=img_url, meta=meta)

    def get_images(self, response, request, info):
        for key, image, buf in super(MyImagesPipeline, self).get_images(response, request, info):
            key = self.file_path(request)
            yield key, image, buf
