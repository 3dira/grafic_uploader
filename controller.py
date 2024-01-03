import os
from deep_translator import GoogleTranslator
from email.headerregistry import ContentTypeHeader
from requests_toolbelt import MultipartEncoder
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
import db
import var
import json
import requests
import re

# Get tags and categories from API
# edit 50 if number of tags is more than 50
url = "https://boomilia.com/api/tags/?limit=50"
response = requests.get(url)
tags = dict(response.json())['results']
url = "https://boomilia.com/api/categories/"
response = requests.get(url)
categories = list(response.json())

# init databse
db.init_db()

# load config file for token and etc
config = {}
with open('conf.json', 'r') as f:
    config = json.load(f)


def send_msg(chat_id, text):
    token = config["token"]
    url_req = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"
    results = requests.get(url_req)


async def send_list_categories(update: Update, post: dict):
    # add tags to bot keyboard buttons
    keys = [[var.command_end_categories, var.input_your_password]]
    for category_dict in categories:
        if category_dict['section'] == post['section']:
            keys.append([category_dict['name']])

    await update.message.reply_text(var.select_your_categories,
                                    reply_markup=ReplyKeyboardMarkup(keys, resize_keyboard=True))


# Check user has been logged in or not


async def check_user(user_id, update: Update):
    user_information = db.get_user(user_id)

    if user_information == None:
        db.create_user(user_id)
        await update.message.reply_text(var.send_your_phone_number)
        return 0
    else:
        session = requests.session()
        if update.message.text == var.command_exit_user:  # user wants to logout
            db.update_user(
                user_id, {'active': '0'})
            await update.message.reply_text(var.you_logged_out_successfully, reply_markup=ReplyKeyboardRemove())
            return 0

        if user_information['phone_number'] == None:
            phone_number = update.message.text
            url = "https://boomilia.com/accounts/send/otp/"
            response = session.get(url)
            response = session.post(url, json={'phone_number': phone_number})
            if response.status_code == 301:  # successfully, code sent
                sessionid = response.cookies.get('sessionid')
                db.update_user(
                    user_id, {'phone_number': phone_number, 'sessionid': sessionid})
                await update.message.reply_text(var.send_your_otp_code)
            else:
                await update.message.reply_text(var.phone_number_not_verified)

            return 0

        if user_information['csrftoken'] == None:
            otp = update.message.text
            sessionid = user_information['sessionid']
            session.cookies.set('sessionid', sessionid)
            url = "https://boomilia.com/accounts/check/otp/"
            response = session.get(url)
            response = session.post(url, json={'otp': otp})
            if response.status_code == 200:  # otp code is correct
                sessionid = response.cookies.get('sessionid')
                csrftoken = response.cookies.get('csrftoken')
                db.update_user(
                    user_id, {'csrftoken': csrftoken, 'sessionid': sessionid})
                await update.message.reply_text(var.successfully_logged_in, reply_markup=var.default_keyboard)
            elif response.status_code == 401:  # otp code isn't correct
                await update.message.reply_text(var.otp_is_not_correct)
            elif response.status_code == 403:  # otp code expired
                url = "https://boomilia.com/accounts/send/otp/"
                response = session.get(url)
                response = session.post(
                    url, json={'phone_number': phone_number})

                await update.message.reply_text(var.otp_timed_out)

            return 0


def between_callback(update: Update, post, user_information, loop):
    try:
        session = requests.session()
        session.headers['Referer'] = 'https://boomilia.com/api/post/'
        csrftoken = user_information['csrftoken']
        sessionid = user_information['sessionid']
        session.cookies.set('csrftoken', csrftoken)
        session.cookies.set('sessionid', sessionid)
        session.headers['X-Csrftoken'] = csrftoken
        post['title'] = "hihi" if post['title'].strip() == '' else post['title']
        fields = [
            ('title', post['title']),
            ('body', post['body']),
            ('technical_tips', post['technical_tips']),
        ]
        for media in post['medias']:
            fields.append(
                ('create_media',
                 (media['name'], open(media['photo'], 'rb'), media['mime'])
                 )
            )
        for tag in post['tags']:
            fields.append(('tags', tag['id']))
        for category in post['categories']:
            fields.append(('category', category['slug']))
        if post['password']:
            fields.append(('password', post['password']))
        if post['has_public_pack']:
            fields.append(
                ('public_pack', (post['public_pack'].get('name', 'package.zip'),
                                 open(post['public_pack']['pack'], 'rb'), post['public_pack']['mime']))
            )
        multipart_data = MultipartEncoder(
            fields=tuple(fields)
        )
        url = 'https://boomilia.com/api/post/'
        request = session.post(url, data=multipart_data, headers={
            'Content-Type': multipart_data.content_type})
        tag_names = []

        post['complate'] = True

        for tag in post['tags']:
            tag_names.append(tag['name'])
        category_names = []
        for category in post['categories']:
            category_names.append(category['name'])
        if request.status_code == 201:  # the post uploded
            send_msg(update.message.chat.id, var.your_post_uploaded.format(post['title']))

            # Send log to admins
            for chat_id in config['admins_chat_id']:
                try:
                    send_msg(chat_id,
                             var.user_uploaded_a_post(update.message.from_user.username, post['title'], post['body'],
                                                      post['technical_tips'], tag_names, category_names))
                except Exception:
                    pass
        else:
            for msg_id in [post['photo_msg_id'], post['doc_msg_id']]:
                loop.create_task(
                    update._bot.forward_message(var.group_blank_title_send, update.message.chat.id, msg_id))
            send_msg(var.group_blank_title_send,
                     var.your_post_was_not_uploaded(request.text) + f"\n\nChat ID: {update.message.chat.id}")
            send_msg(update.message.chat.id, var.your_post_was_not_uploaded(request.text))

            for chat_id in config['admins_chat_id']:

                try:
                    send_msg(chat_id, var.user_can_not_upload_a_post(update.message.from_user.username, post['title'],
                                                                     post['body'], post['technical_tips'], tag_names,
                                                                     category_names, request.text))
                except Exception:
                    pass

    except Exception as e:
        print(e)
        send_msg(update.message.chat.id, var.try_again_your_command_was_bad)

    for media in post['medias']:
        try:
            os.unlink(media['photo'])
        except Exception as e:
            pass
    if post['has_public_pack']:
        try:
            os.unlink(post['public_pack']['pack'])
        except Exception as e:
            pass


def TextTranslator(text):
    try:
        translated = GoogleTranslator(source='auto', target='fa').translate(text)
        if translated: return translated
    except Exception as e:
        print(e)
    if text:
        return text
    return "empty"


def remove_hashtags(text):
    return re.sub(r'#\w+', '', text.replace("_", "").replace("-", "").replace("/", ""))


def find_category(categories, category, post):
    for _category in categories:
        if _category["name"] == category and _category['section'] == post['section']:
            return _category
        else:
            result = find_category(_category["sub_categories"], category, post)
            if result is not None:
                return result
    return None


def auto_category_select(caption, post):
    category_dict = {
        "Office,furniture,chair": "صندلی اداری",
        "Arm_Chair,ArmChair": "صندلی دسته دار",
        "Arm_Chair,ArmChair,clasicc": "صندلی دسته دار کلاسیک",
        "office,workplace": "میز صندلی اداری",
        "furniture,bathroom": "روشوی مدرن",
        "ceramic": "کاشی  و سرامیک",
        "flowers": "گیاهان تزئینی",
        "Decoration  Sculpture": "مجسمه",
        "TV Wall": "دیوار تلویزیون مدرن",
        "motor,ycle": "دوچرخه و موتور سیکلت",
        "wardrobe": "کمد دیواری و دکوری مدرن",
        "Lighting": "لوستر مدرن",
        "wallpaper": "کاغذ دیواری",
        "console": "آینه کنسول و میز آرایش",
        "Table,classical": "میز کلاسیک",
        "Building": "ساختمان 3d",
        "Table,Chair": "میز صندلی مدرن",
        "Shop,lunch,store,fast_food,refrigerator": "تجهیزات فروشگاهی",
        "bath,water,jacuzzi": "وان حمام",
        "tile,mosaic": "کاشی  و سرامیک",
        "tube,soap,pump,jar,sanco,cosmetics,bottle,shampoo,gel": "اکسسوری مدرن حمام",
        "bed,linens,pillows,nightstand": "تخت خواب مدرن",
        "glass_block": "دکوری",
        "curtain": "پرده مدرن",
        "tile,marble": "سنگ ها",
        "Lighting,Wall": "دیوارکوب مدرن",
        "lamp,floor": "آباژور ایستاده مدرن",
        "table-lamp": "آباژور مدرن",
        "table,lamp": "آباژور مدرن",
        "childrens,teenage,closet": "کمد دیواری و میز تحریر",
        "bag,gucci,travel,clothes": "پوشاک",
        "decoration,mirror": "قاب آینه مدرن",
        "Bathroom_accessories": "اکسسوری مدرن حمام",
        "furniture,bathroom,sink,classic": "روشوی کلاسیک",
        "fabric,cotton,textile,texture,material,seamless": "چرم-پارچه-فرش",
        "Shop,lunch,store,fast_food,refrigerator": "تجهیزات فروشگاهی",
        " bath,water,jacuzzi": "وان حمام",
        "tile,mosaic": "کاشی  و سرامیک",
        "drum": "لوازم موسیقی",
        "tube,soap,pump,jar,sanco,cosmetics,bottle,shampoo,gel": "اکسسوری مدرن حمام",
        "bed,linens,pillows,nightstand": "تخت خواب مدرن",
        "doors": "درب مدرن",
        "glass_block": "دکوری",
        "curtain": "پرده مدرن",
        "tile,marble": "سنگ ها",
        "Lighting,Wall": "دیوارکوب مدرن",
        "lamp,floor": "آباژور ایستاده مدرن",
        "table-lamp": "آباژور مدرن",
        "table,lamp": "آباژور مدرن",
        "pouf": "پاف",
        "childrens,teenage,closet": "کمد دیواری و میز تحریر",
        "decoration": "دکوری",
        "bag,gucci,travel,clothes": "پوشاک",
        "Ottoman": "پاف",
        "stone": "سنگ ها",
        "decoration,mirror": "قاب آینه مدرن",
        "Bathroom_accessories": "اکسسوری مدرن حمام",
        "furniture,bathroom,sink,classic": "روشوی کلاسیک",
        "fabric,cotton,textile,texture,material,seamless": "چرم-پارچه-فرش",
        "elevator": "آسانسور",
        "chandelier": "لوستر مدرن",
        "bagbusiness": "پوشاک",
        "Plants": "درختان",
        "Spot_light": "هالوژن مدرن",
        "street_tree": "درختان",
        "Other_kitchen_accessories": "آبجکتهای دکوری آشپزخانه",
        "knob": "دستگیره",
        "chairs,armchair,office": "صندلی اداری",
        "Childroom,Toy": "اسباب بازی های کودکانه",
        "pot,plant,greens": "گیاهان تزئینی",
        "Plants,Outdoor": "درختان",
        "TV_Wall,tv,wall": "دیوار تلویزیون مدرن",
        "audio,speakers,wireless,Audioengine": "لوازم الکتریکی یا برقی",
        "mid_tower,pc,corsair": "تلویزیون و کامپیوتر",
        "Street,lighting,lamp": "روشنای محوطه مدرن",
        "monitor,display": "تلویزیون و کامپیوت",
        "Floor,lamp": "آباژور ایستاده مدرن",
        "products,tv": "تلویزیون و کامپیوتر",
        "Wall_light": "دیوارکوب مدرن",
        "Decor,Sculptures,heron,bronze,bird": "مجسمه",
        "Decor,Sculptures": "مجسمه",
        "Bathroom,accessories": "اکسسوری مدرن حمام",
        "roof,sandwich,panel": "ابجکتهای معماری محوطه مدرن",
        "brick": "آجر",
        "toilet": "توالت",
        "bedroom,bed,natuzzi": "تخت خواب مدرن",
        "toy": "اسباب بازی های کودکانه",
        "bird": "حیوانات",
        "Doors,east,arab": "درب کلاسیک",
        "reception": "میز صندلی منشی یا پذیرش",
        "table,classic": "میز کلاسیک",
        " power,lines": "ابجکتهای معماری محوطه مدرن",
        "chandelier": "لوستر مدرن",
        "Architecture,Fence": "ابجکتهای معماری محوطه مدرن",
        "chair": "صندلی",
        "Sofa": "مبل مدرن",
        "Table": "میز",
        "laminate": "چوب و پارکت",
        "pouf": "پاف",
        "stone": "سنگ ها",
        "Ottoman": "پاف",
        "decoration": "دکوری",
        "doors": "درب مدرن",
        "drum": "لوازم موسیقی",
        "Bush": "بوته",
        "Carpets": "فرش ها",
        "truck": "کامیون",
        "railing": "نرده مدرن",
    }
    for category in category_dict:
        word_lst = category.split(",")
        exist_word = [x for x in word_lst if x.lower() in caption.lower()]

        if len(word_lst) == len(exist_word):
            findCategory = find_category(categories, category_dict[category], post)
            if findCategory:
                return findCategory
    return None
