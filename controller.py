import asyncio,os
from email.headerregistry import ContentTypeHeader
from requests_toolbelt import MultipartEncoder
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
import db
import requests
import var
import json
import requests

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

def send_msg(chat_id,text):
    token = config["token"]
    url_req = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"
    results = requests.get(url_req)
    

async def send_list_categories(update: Update, post: dict):
    # add tags to bot keyboard buttons
    keys = [[var.command_end_categories]]
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


def between_callback(update,post,user_information):
    try:
        session = requests.session()
        session.headers['Referer'] = 'https://boomilia.com/api/post/'
        csrftoken = user_information['csrftoken']
        sessionid = user_information['sessionid']
        session.cookies.set('csrftoken', csrftoken)
        session.cookies.set('sessionid', sessionid)
        session.headers['X-Csrftoken'] = csrftoken
        fields = [
            ('title', post['title']),
            ('body', post['body']),
            ('technical_tips', post['technical_tips']),
        ]
        for media in post['medias']:
            
            fields.append(
                ('create_media',
                (media['name'], open(media['photo'], 'rb'),media['mime'])
                )
            )
        for tag in post['tags']:
            fields.append(('tags', tag['id']))
        for category in post['categories']:
            fields.append(('category', category['slug']))
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
            send_msg(update.message.chat.id ,var.your_post_uploaded.format(post['title']))
            
            # Send log to admins
            for chat_id in config['admins_chat_id']:
                try:
                    send_msg(chat_id ,var.user_uploaded_a_post(update.message.from_user.username, post['title'], post['body'], post['technical_tips'], tag_names, category_names))
                except Exception:pass
        else:
            send_msg(update.message.chat.id ,var.your_post_was_not_uploaded(request.text))

            for chat_id in config['admins_chat_id']:
                
                try:
                    send_msg(chat_id ,var.user_can_not_upload_a_post(update.message.from_user.username, post['title'], post['body'], post['technical_tips'], tag_names, category_names,  request.text))
                except Exception:pass
        
    except Exception as e:
        print(e)
        send_msg(update.message.chat.id ,var.try_again_your_command_was_bad)
    for media in post['medias']:
        try:os.unlink(media['photo'])
        except Exception as e:pass
    if post['has_public_pack']:
        try:os.unlink(post['public_pack']['pack'])
        except Exception as e:pass
