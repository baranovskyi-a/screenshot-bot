from aiogram import Bot, Dispatcher, types, executor
from config import TOKEN
import validators
from selenium import webdriver
from PIL import Image
from io import BytesIO
import base64
from time import sleep

bot = Bot(TOKEN)
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


@dp.message_handler()
async def make_screen(message: types.Message):
    if not validators.url(message.text):
        await bot.send_message(message.from_user.id, 'Url is not valid')
        return None

    driver = webdriver.Safari()
    driver.set_page_load_timeout(10)
    driver.get(message.text)
    max_width = 1920
    max_height = 8080
    screen_width = max_width
    screen_height = driver.execute_script('return Math.max('
                                          'document.body.scrollHeight, '
                                          'document.body.offsetHeight, '
                                          'document.documentElement.clientHeight, '
                                          'document.documentElement.scrollHeight, '
                                          'document.documentElement.offsetHeight);')
    driver.set_window_size(screen_width, screen_height)
    body = driver.find_element_by_tag_name('body')
    # remove_fixed_elements(driver, body)

    b64str = driver.get_screenshot_as_base64()
    driver.quit()
    im = Image.open(BytesIO(base64.b64decode(b64str)))
    if im.size[0] > max_width or im.size[1] > max_height:
        divider = max(im.size[0]/max_width, im.size[1]/max_height)
        im = im.resize(size=(int(im.size[0]/divider), int(im.size[1]/divider)))
    bio = BytesIO()
    bio.name = 'image.png'
    im.save(bio, 'PNG')
    bio.seek(0)
    await bot.send_photo(message.from_user.id, photo=bio)



if __name__ == '__main__':
    executor.start_polling(dp)
