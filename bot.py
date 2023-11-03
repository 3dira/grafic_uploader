import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler
from requests_toolbelt.multipart.encoder import MultipartEncoder
import threading  
from pathlib import Path 
import var
import db
import controller
from controller import send_list_categories, tags, categories, config

posts = []
def get_last_post(user_id):
    for post in reversed(posts):
        if post['user'] == user_id:return post
    return {}
def delete_post(user_id):
    for index_post ,post in enumerate(posts):
        if post["user"] == user_id: posts.pop(index_post)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    try:
        if update.message.from_user.is_bot:
            return

        user_id = str(update.message.from_user.id)

        user_information = db.get_user(user_id)
        message = update.message.text

        if update.message.text == var.command_help:
            await update.message.reply_text(var.help_text)
            return

        status = await controller.check_user(user_id, update)
        if status == 0:  return

        if update.message.photo:  # User has sent a photo
            post = get_last_post(user_id)
            if post and not post.get('complate'):
                if not post['end_media']:
                    media = await update.message.photo[-1].get_file(read_timeout=60)
                    
                    media_path = config['base_path']+'/'+media.file_path.split(
                        '/')[0]+'/'+media.file_path.split('/')[-2]+'/'+media.file_path.split('/')[-1]
                    
                    caption_image_space = update.message.caption.split()
                    caption_image_line = [x for x in update.message.caption.replace("  ","\n").split("\n") if x]
                    hash = caption_image_line[0] if len(caption_image_line) >= 3 else caption_image_space[0] if len(caption_image_space) >= 3 else "empty"
                    post['medias'].append(
                        {'photo': media_path, 'mime': 'image/png', 'name': 'image.png',"caption" : update.message.caption,"obj":media,"hash" : hash})
                    post['end_media'] = True
                    if update.message.caption:
                        post["title"] = caption_image_line[1] if len(caption_image_line) >= 3 else caption_image_space[1] if len(caption_image_space) >=3 else "empty" 
                    
                    await update.message.reply_text(var.get_a_photo,reply_to_message_id=update.message.id)
                else :
                    await update.message.reply_text("تصویر از قبل برای این پست تنظیم شده است .", reply_to_message_id=update.message.id)
            return
            
        if update.message.document: 
            post = get_last_post(user_id)
            if post and post['has_public_pack'] :
                if not post['public_pack']:
                    package = await update.message.document.get_file(read_timeout=10000)
                    package_path = config['base_path']+'/'+package.file_path.split(
                        '/')[0]+'/'+package.file_path.split('/')[-2]+'/'+package.file_path.split('/')[-1]
                    
                    package_name = Path(update.message.document.file_name).stem
                    if post["medias"] and not package_name in post["medias"][0]["caption"]:
                        caption_image_space = post['medias'][0]['caption'].split()
                        caption_image_line = [x for x in post['medias'][0]['caption'].replace("  ","\n").split("\n") if x]
                        
                        id_f = caption_image_line[0] if len(caption_image_line) >= 3 else caption_image_space[0] if len(caption_image_space) >= 3 else "empty"
                        await update.message.reply_text(f"فایل ارسالی مربوط به عکس ارسالی نمیشود لطفا فایل را اصلاح کنید \nایدی عکس مربوطه {id_f} \nآیدی فایل مربوطه : {package_name}")
                        return
                    post['public_pack'] = {
                        "obj":package,
                        'name': update.message.document.file_name,
                        'pack': package_path, 'mime': update.message.document.mime_type
                    }
                    await update.message.reply_text(var.get_a_package, reply_to_message_id=update.message.id)
                    await send_list_categories(update, post)
                else :
                    await update.message.reply_text("فایل از قبل برای این پست تنظیم شده است .", reply_to_message_id=update.message.id)
            return
        
        if update.message.text:
            if update.message.text == var.command_new_post:
                posts.append({'user': user_id,
                            'complate': False,
                            'medias': [], 
                            'end_media': False,
                            'send_link': False,
                            'title': '',
                            'tags': [{'id': str(18), 'name': "گرافیک"}], 
                            'tags_complate': True,
                            'categories': [], 
                            'categories_complate': False,
                            'has_public_pack': True, 
                            'public_pack': '',
                            'body': '', 
                            'technical_tips': '',
                            'has_body': False, 
                            'has_technical_tips': False,
                            'section': "graphic", 
                            })
                await update.message.reply_text(var.send_your_media,reply_markup=var.media_mode_keyboard)
                return
            
            post = get_last_post(user_id)
            
            if update.message.text == var.command_remove_post:  # delete the post
                delete_post(user_id)
                await update.message.reply_text(var.your_post_deleted_successfully, reply_markup=var.default_keyboard)
                return
            if update.message.text == var.command_end_categories:
                if (post['section'] == '3d' or post['section'] == 'graphic') and\
                        len(post['categories']) == 0:
                    await update.message.reply_text(var.you_should_select_a_category)
                    return
                post['categories_complate'] = True
                await update.message.reply_text(var.upload_your_post, reply_markup=var.upload_post_keyboard)
                return
            if update.message.text == var.command_upload_post:
                if post['has_public_pack'] and post['public_pack'] == '':
                    await update.message.reply_text(var.please_send_your_package)
                    return
                await update.message.reply_text(var.your_post_is_uploading,reply_markup=var.default_keyboard)
                post = get_last_post(user_id)
                print(post["categories"])
                thread = threading.Thread(target=controller.between_callback,args=(update,post,user_information,))
                thread.start()
                print(post)
                delete_post(user_id)
                return
            if post and not post['complate'] and not post.get('categories_complate'):
                if post['public_pack'] and post['end_media']:
                    category = update.message.text
                    category_slug = ''
                    if update.message.text == var.command_back_to_list_categories:
                        await send_list_categories(update, post)
                        return
                    def find_category(categories, category):
                        for _category in categories:
                            if _category["name"] == category:
                                return _category
                            else:
                                result = find_category(_category["sub_categories"], category)
                                if result is not None:
                                    return result
                        return None

                    result = find_category(categories, category)      
                    if result and not result["sub_categories"]: 
                        category_slug = result['slug']
                    else:
                        childs = []
                        if result:
                            for category_sub in result['sub_categories']:
                                childs.append([category_sub['name']])
                            reply_markup = var.keyboard_select_child_categories(
                                childs)
                            await update.message.reply_text(var.select_your_child_categories, reply_markup=reply_markup)
                            return
                    if not result:
                        await update.message.reply_text(var.your_category_was_not_found)
                        return
                    if not category_slug:return
                    post['categories'].append(
                        {'slug': str(category_slug), 'name': category})
                    await update.message.reply_text(var.your_category_added)
                else :
                    await update.message.reply_text(var.please_send_your_package)
                return

        await update.message.reply_text(var.i_am_bot,
                                        reply_markup=var.default_keyboard)
        delete_post(user_id)
    except Exception as e:
        print(e)
        delete_post(user_id)
        await update.message.reply_text(var.try_again_your_command_was_bad,reply_markup=var.default_keyboard)
        

app = ApplicationBuilder().token(config['token'])

# if config['use_local_server']:app = app.base_url(config['base_url']).base_file_url("").local_mode(True)
if config['use_proxy']:
    proxy_url = config['proxy_url']
    app = app.proxy_url(proxy_url).get_updates_proxy_url(proxy_url)

app = app.build()

app.add_handler(MessageHandler(None, message_handler, block=False))

app.run_polling()
