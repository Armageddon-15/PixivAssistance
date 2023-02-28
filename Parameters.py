from PAEnum import NamingMethod


utc_offset = 8

data_extension = ".ill"
gif_extension = ".webp"
naming_method = NamingMethod.by_index

'''login token'''
login_token_path = "login_token"

'''path'''
illust_data_path = "data\\"
illust_thbnl_path = "thumbnails\\"
illust_cache_path = "cache\\"
icon_path = "icons\\"
auth_head_path = "auth\\"
download_path = "G:\\AnimPic_Unsorted\\Pictures 91\\"
r18_subfolder = "R-18\\"
# gif_path = "D:\\PhonePicBackUp\\GIFs\\"
gif_path = download_path
# group_path = "G:\\AnimPic_Unsorted\\set pics\\"
group_path = download_path
special_tags_config_path = "special_tags.config"

path_list = [illust_data_path, illust_thbnl_path, illust_cache_path, download_path, auth_head_path,
             download_path + r18_subfolder, gif_path + r18_subfolder, group_path + r18_subfolder]

'''download param'''
max_download_thread = 4
check_downloaded = False

'''PA load setting'''
# currently not support list attribute such as tags and translated_tags
# method should be "or" or "and", default is "or"
# pa_load = {"method": "and", "is_like": False, "is_nsfw": False}
pa_load = {}


'''proxy'''
proxies = {
    'https': 'socks5://127.0.0.1:1080',
    'http': 'socks5://127.0.0.1:1080'
}
