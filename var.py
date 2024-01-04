# This file is only for define some variables
from telegram import ReplyKeyboardMarkup
import json

# Load configs
config = {}
with open('conf.json', 'r') as f:
    config = json.load(f)

group_blank_title_send = -1002125821324
# Commands
add_public_package = 'افزودن پکیج'
do_not_have_description = 'توضیحات ندارم'
do_not_have_technical_tips = 'توضیحات فنی ندارم'
command_help = "راهنما"
command_remove_post = "حذف پست"
command_new_post = "پست جدید"
command_end_media = "اتمام عکس/فیلم"
command_upload_post = "آپلود پست"
command_end_tags = "اتمام تگ"
command_end_categories = "اتمام دسته بندی"
input_your_password = "پسوورد فایل"
command_exit_user = "خروج از حساب کاربری"
command_back_to_list_categories = "بازگشت"
command_send_link_file = "ارسال لینک پست اینستاگرام"
skip = "رد شو"

pls_enter_your_password = "لطفا پسوورد فایل را وارد کنید:"
password_was_set = "پسوورد فایل به {password} تغییر پیدا کرد."

media_mode_keyboard_list = [
    [command_remove_post]
]
if config.get('use_instagram', False):
    media_mode_keyboard_list[0].append(command_send_link_file)

default_keyboard = ReplyKeyboardMarkup(
    [[command_help, command_new_post], [command_exit_user]], resize_keyboard=True)
media_mode_keyboard = ReplyKeyboardMarkup(
    media_mode_keyboard_list, resize_keyboard=True, one_time_keyboard=True)
skip_keyboard = ReplyKeyboardMarkup(
    [[skip], [command_remove_post]], resize_keyboard=True, one_time_keyboard=True
)
back_btn = ReplyKeyboardMarkup(
    [[command_back_to_list_categories]], resize_keyboard=True, one_time_keyboard=True
)
upload_post_keyboard = ReplyKeyboardMarkup([
    [command_upload_post],
    [command_remove_post]
], resize_keyboard=True, one_time_keyboard=True)
upload_post_keyboard_with_pack = ReplyKeyboardMarkup([
    [command_upload_post],
    [add_public_package],
], resize_keyboard=True, one_time_keyboard=True)
description_send_keyboard = ReplyKeyboardMarkup([
    [do_not_have_description],
], resize_keyboard=True, one_time_keyboard=True)
technical_tips_send_keyboard = ReplyKeyboardMarkup([
    [do_not_have_technical_tips],
], resize_keyboard=True, one_time_keyboard=True)


def keyboard_select_child_categories(childs):
    return ReplyKeyboardMarkup([
                                   [command_back_to_list_categories],
                               ] + childs, resize_keyboard=True)


help_text = """
1- هر موقع که به راهنمایی نیاز داشتید کلمه راهنما را بفرستید.
2- جهت ایجاد پست جدید عبارت پست جدید به بفرستید.
2-1- در مرحله اول از شما درخواست می شود که عکس های پست خودتان را بفرستید.
2-2- پس از اینکه عکس(های) پست خود را فرستادید عبارت اتمام عکس را بفرستید.
2-3- سپس شما باید موضوع پست خودتان را مشخص کنید.
2-4- سپس از شما خواسته می شود که تگ های مورد نظر خودتان را وارد کنید.
2-5- پس از اتمام وارد کردن تگ ها عبارت اتمام تگ را بفرستید.
2-6- دسته بندی دقیقا مثل تگ از شما خواسته می شود و پس از اتمام وارد کردن دسته بندی ها عبارت اتمام دسته بندی را بفرستید.
2-7- سپس توضیحات خود را بفرستید و در آخر عبارت آپلود پست را بفرستید.

پیشنهادات و انتقادات خودتان را به پشتیبانی بومیلیا بگویید.
تمام حقوق محفوظ است https://boomilia.com
طراح و توسعه دهنده: @motahharmokfi
"""

phone_number_not_verified = """
شماره تلفن شما صحیح نیست.
1- مطمئن شوید که در https://boomilia.com ثبت نام کرده اید
2- شماره تلفن خود را با اعداد لاتین وارد کرده اید
3- شماره تلفن خود را به صورت کامل وارد کردهاید

در صورتی که مشکل شما حل نشد به پشتیبانی سایت بومیلیا اطلاع دهید.
"""

send_your_media = """
لطفا عکس و فایل خودتان را برای من ارسال کنید.
شما می توانید عکس یا ویدئو را فروارد کنید.\n
همچنین دقت کنید که در هر مرحله می تواند عبارت حذف پست را بفرستید تا پست شما حذف شود.
"""

your_post_uploaded = """
پست شما با موضوع {} با موفقیت آپلود شد.
پس از بررسی توسط ادمین های سایت بومیلیا روی سایت منتشر می شود.
"""

send_your_phone_number = "لطفا شماره خودتان را بفرستید."
send_your_otp_code = "لطفا کد ارسال شده به شماره همراه خودتان را وارد کنید.\nلطفا کد را به لاتین وارد کنید."
send_your_description = "لطفا توضیحات خود را وارد کنید.\nدقت کنید شما توضیحات شما نباید بیشتر از 1024 حرف باشد."
send_your_technical_tips = "لطفا توضیحات فنی خود را وارد کنید.\nدقت کنید شما توضیحات فنی شما نباید بیشتر از 1024 حرف باشد."
select_your_categories = "لطفا دسته بندی های مورد نظر خود را انتخاب کنید و سپس اتمام دسته بندی را بزنید."
select_your_child_categories = "دسته بندی که انتخاب کردید زیر مجموعه دارد.\nلطفا از زیر مجموعه های آن یک مورد را انتخاب کنید."
select_your_tags = "لطفا تگ های مورد نظرتان را انتخاب کنید و در انتها اتمام تگ را بزنید.\nدر صورتی که می خواهید پکیج اضافه کنید باید تگ 3d یا مهندسی را انتخاب کنید."
send_your_post_title = "موضوع پست خودتان را ارسال کنید."
send_your_package = "لطفا پکیج خودتان را بفرستید.\nفرمت های پشتیبانی شده: zip, rar, 7z"
send_your_media_url = "لطفا لینک پست اینستاگرام خود را بفرستید."
successfully_logged_in = "با موفقیت وارد حساب کاربری خود شدید.\n" + help_text
otp_is_not_correct = "کد وارد شده صحیح نمی باشد.\nلطفا کد را به لاتین وارد کنید."
otp_timed_out = "زمان اعتبار کد به پایان رسیده است. لطفا کد ارسال شده جدید را وارد کنید."
get_a_photo = "عکس با موفقیت دریافت شد ."
get_a_video = "ویدئو شما دریافت شد."
get_a_package = "پکیج با موفقیت دریافت شد ."
you_should_select_a_category = "شما تگ گرافیک یا 3d را انتخاب کرده اید بنابراین شما باید حداقل یک دسته بندی انتخاب کنید"
you_does_not_send_any_photo = "شما هیچ عکس یا ویدئویی را نفرستاده اید."
you_logged_out_successfully = "با موفقیت از حساب کاربری خودتان خارج شدید.\nبرای شروع دوباره /start را بزنید."
your_tag_added = "تگ مورد نظر شما به لیست تگ های این پست افزوده شد."
your_tag_was_not_found = "تگ مورد نظر شما پیدا نشد."
your_category_added = "دسته بندی مورد نظر شما به لیست دسته بندی های این پست افزوده شد."
your_category_was_not_found = "دسته بندی مورد نظر شما پیدا نشد."
your_post_deleted_successfully = "پست شما با موفقیت حذف شد."
your_post_is_uploading = "پست شما در حال آپلود است.\nنتیجه پس از آپلود به شما اطلاع رسانی خواهد شد."
your_description_is_big = "توضیحات شما بیشتر از 1024 کاراکتر است!\nلطفا دوباره توضیحات خود را بفرستید."
your_technical_tips_is_big = "توضیحات فنی شما بیشتر از 1024 کاراکتر است!\nلطفا دوباره توضیحات فنی خود را بفرستید."
your_package_is_not_supported = "پکیجی که آپلود کرده اید پشتیبانی نمی شود.\nلطفا به @Boomiliaco اطلاع دهید."
your_package_is_downloading_please_wait = "پکیج شما در حال دریافت است.\nلطفا صبر کنید..."
your_instagram_posts_loaded = "پست اینستاگرام شما لود شد."
your_link_is_not_crrect = "لینک پست اینستاگرام شما صحیح نیست. لطفا دوباره آن را بفرستید."
please_send_your_package = "لطفا ابتدا پکیج خود را ارسال کنید و مطمئن شوید که ربات پکیج شما را دریافت کرده است."
upload_your_post = "پست شما آماده شد.\nجهت آپلود روی آپلود پست بزنید"
i_am_bot = "سلام خوش آمدید.\nربات بومیلیا هستم.\nhttps://boomilia.com\nجهت آپلود پست در وبسایت بومیلیا می توانید از من استفاده کنید."
try_again_your_command_was_bad = "درخواست شما اجرا نشد\nلطفا مجددا تلاش کنید.\nتیم پشتیبانی @Boomiliaco"


# Admin logs
def user_deleted_a_post(username): return f"""
پیام مخصوص ادمین های بات

کاربر @{username} می خواست پستی را آپلود کند اما منصرف شد و آن را حذف کرد.
"""


def user_uploaded_a_post(username, title, body, technical_tips, tag_names, category_names): return f"""
پیام مخصوص ادمین های بات

کاربر @{username} پست جدیدی را با موفقیت آپلود کرد.
موضوع: {title}

توضیحات: {body}

توضیحات فنی: {technical_tips}

تگ ها: {','.join(tag_names)}
دسته بندی ها: {','.join(category_names)}
"""


def user_can_not_upload_a_post(username, title, body, technical_tips, tag_names, category_names,
                               response_text): return f"""
پیام مخصوص ادمین های بات

کاربر @{username} می خواست پستی را آپلود کند اما موفق نشد.
موضوع: {title}

توضیحات: {body}

توضیحات فنی: {technical_tips}

تگ ها: {','.join(tag_names)}
دسته بندی ها: {','.join(category_names)}

ادمین گرامی لطفا پیگیری بفرمایید.
ریسپانس سرور بومیلیا: {response_text}
"""


def your_post_was_not_uploaded(response):
    return "پست شما آپلود نشد.\nریسپانس سرور بوملیا: " + response

# add_public_package = "Add package"
# do_not_have_description = "I do not have description"
# do_not_have_technical_tips = "I do not have technical tips"
# command_help = "help"
# command_remove_post = "Delete post"
# command_new_post = "New post"
# command_end_media = "End media"
# command_upload_post = "Upload post"
# command_end_tags = "End tag"
# command_end_categories = "End category"

# default_keyboard = ReplyKeyboardMarkup(
#     [[command_help, command_new_post]], resize_keyboard=True)
# media_mode_keyboard = ReplyKeyboardMarkup([
#     [command_end_media, command_remove_post]
# ], resize_keyboard=True,  one_time_keyboard=True)
# upload_post_keyboard = ReplyKeyboardMarkup([
#     [command_upload_post],
# ], resize_keyboard=True, one_time_keyboard=True)
# upload_post_keyboard_with_pack = ReplyKeyboardMarkup([
#     [command_upload_post],
#     [add_public_package],
# ], resize_keyboard=True, one_time_keyboard=True)
# description_send_keyboard = ReplyKeyboardMarkup([
#     [do_not_have_description],
# ], resize_keyboard=True, one_time_keyboard=True)
# technical_tips_send_keyboard = ReplyKeyboardMarkup([
#     [do_not_have_technical_tips],
# ], resize_keyboard=True, one_time_keyboard=True)


# help_text = """
# 1- Whenever your need help, Just send help message.
# 2- If you want to create a new post send New post.

# Send your ideas and comments in boomilia.
# Copy Right https://boomilia.com
# Developer: @motahharmokfi
# """

# phone_number_not_verified = """
# Your phone number isn't correct.
# 1- Are your registered in https://boomilia.com ??
# 2- Send your phone number with latin numbers.
# 3- Send your phone number correct.

# Any problem?? Send your problem to @Boomiliaco
# """

# send_your_media = """
# Send your photos and videos for me.
# You can forward them for me.
# """

# send_your_phone_number = "Please send your phone number."
# send_your_otp_code = "Send your code that have sent for your phone number."
# send_your_description = "Send your description."
# send_your_technical_tips = "Send your technical tips."
# select_your_categories = "Select your categories."
# select_your_tags = "Select your tags"
# sent_your_post_title = "Send your posts' title"
# send_your_package = "Send your package"
# successfully_logged_in = "You have logged in :)\n"+help_text
# otp_is_not_correct = "Your code isn't correct"
# otp_timed_out = "Your code expired.\nPlease send new code."
# get_a_photo = "You send a photo"
# get_a_video = "You send a video"
# get_a_package = "You have sent package"
# you_should_select_a_category = "Your should select a category."
# you_does_not_send_any_photo = "You don't have any photo or video."
# your_tag_added = "Your tag added."
# your_tag_was_not_found = "Your tag was not found."
# your_category_added = "Your selected category added."
# your_category_was_not_found = "Your category was not found."
# your_post_uploaded = "Your post uploaded successfuly."
# your_post_was_not_uploaded = "Your post did not upload."
# your_post_deleted_successfully = "Your post removed."
# your_description_is_big = "Your description should not be more than 1024 letters.\nResend your description."
# your_description_is_big = "Your technical tips should not be more than 1024 letters.\nResend your technical tips."
# your_package_is_not_supported = "Your package type doesn't support."
# upload_your_post = "Your post is ready."
# i_am_bot = "Hi, I'm Boomilias' bot\nhttps://boomilia.com"


# # Admin logs
# def user_deleted_a_post(username): return f"""
# This message is for admins.

# @{username} wanted to upload a post but removed it.
# """
# def user_uploaded_a_post(username, title, body, tag_names, category_names): return f"""
# This message is for admins.

# @{username} uploaded a new post.
# title: {title}
# description: {body}
# tags:
# {','.join(tag_names)}
# categories:
# {','.join(category_names)}
# """
# def user_can_not_upload_a_post(username, title, body, tag_names, category_names, response_text): return f"""
# This message is for admins.

# @{username} wanted to upload a post but there is an error.
# title: {title}
# description: {body}
# tags:
# {','.join(tag_names)}
# categories:
# {','.join(category_names)}

# Hey admin please check it
# Response of server: {response_text}
# """
