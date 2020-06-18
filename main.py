from aiogram import Bot, Dispatcher, types, executor
import config
import validators
from PIL import Image
from io import BytesIO
import base64
from time import sleep


bot = Bot(config.TOKEN)
dp = Dispatcher(bot)


def remove_fixed_elements(driver, parent_node):
    if parent_node.value_of_css_property('position') == 'fixed':
        driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, parent_node)
    else:
        child_elements = parent_node.find_elements_by_xpath('./*')
        for element in child_elements:
            remove_fixed_elements(driver, element)


def get_b64_screen_from_url(url, remove_fixed=False):
    driver = config.WEB_DRIVER(quiet=True)
    driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
    driver.get(url)
    sleep(1)
    screen_width = config.MAX_WIDTH
    screen_height = driver.execute_script('return Math.max('
                                          'document.body.scrollHeight, '
                                          'document.body.offsetHeight, '
                                          'document.documentElement.clientHeight, '
                                          'document.documentElement.scrollHeight, '
                                          'document.documentElement.offsetHeight);')
    driver.set_window_size(screen_width, screen_height)
    if remove_fixed:
        body = driver.find_element_by_tag_name('body')
        remove_fixed_elements(driver, body)
    b64str = driver.get_screenshot_as_base64()
    driver.quit()
    return b64str


def get_bytesio_image_from_b64(b64):
    im = Image.open(BytesIO(base64.b64decode(b64)))
    if im.size[0] > config.MAX_WIDTH or im.size[1] > config.MAX_HEIGHT:
        divider = max(im.size[0] / config.MAX_WIDTH, im.size[1] / config.MAX_HEIGHT)
        im = im.resize(size=(int(im.size[0] / divider), int(im.size[1] / divider)))
    bio = BytesIO()
    bio.name = 'image.png'
    im.save(bio, 'PNG')
    bio.seek(0)
    return bio


@dp.message_handler()
async def make_screen(message: types.Message):
    if not validators.url(message.text):
        await bot.send_message(message.from_user.id, 'Url is not valid')
        return None
    b64str = get_b64_screen_from_url(url=message.text, remove_fixed=config.REMOVE_FIXED)
    bio = get_bytesio_image_from_b64(b64=b64str)
    await bot.send_photo(message.from_user.id, photo=bio)


if __name__ == '__main__':
    executor.start_polling(dp)
