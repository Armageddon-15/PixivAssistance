

# HOW TO USE PIXIV ASSISTANCE

## WHY DID I CREATE IT
- I love to watch anime pictures
- pixiv is the most familar website I've known
- mobile proxy is unstable
- it's painful saving pictures in website, especially save tons of.

## WHAT CAN IT DO
### There are two widgets in this gui, *explore widget* and *detail widget*.
#### Explore Widget
Explore widget basically just can watch thumbnail pictures from author who you follow, and you can like it or like&download it. (It's my own habit that like works which I'd like to download) 

like&download button will download all the images if the work have. If you want to download particular one, just go to the detail widget.
#### Detail Widget
Detail widget can show large picture(s), author's name, tags and works' introduction of picture which you click in explore widget. 

There is also the work's title and you can click it to visit the web page of the work, in case you want to make comments on it.

Because I haven't make a automatically load method, you can change the value of the number of images per load.
Press 'N' to load new.

You can download one image by clicking  '↓' at bottom right corner of image or just double click it.(Unfixed bug: when load new pictures, "↓" will move to top left corner)

Download image in this widget will not like the work.


## ANNOUNCEMENT
This is a very first version. And I'm new to programming, so feel free to give me your suggestions :P

## SET-UP STEPS
### Download code
If you use pycharm, download all the file and there you go~
else please download files:`Pixiv_Assistance.py`, `download_thbnl.py`, `reqiurements.txt`, `Refresh_token.py` and folders: `icon`,  `pixivpy3`. And config yourself.(because I don't know how :P)

### Parameters

1.Set parameters both in `Pixiv_Assistance.py`, `download_thbnl.py`
 
you can ref from the table below

|parameter name|usage|data type|
|--|--|--|
|login_token|open `Refresh_token.py` and see [This](https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362)|str
|tag_pre_line|tag(s) per line|int
|stream_per_load|images per load|int
|like_btn_size| size of every button size(not only like)|int
|thumbnail_size|size of thumbnail picture|int
|pic_grid_row|*pic_grid_column = pictures per page|int
|pic_grid_column|*pic_grid_row = pictures per page|int
|nsfw|if open nsfw in *explore widget*|bool
|utc_offset|time zone offset|int
|data_extension|extension of work's data|str
|illust_data_path|path to save data|str
|illust_thbnl_path|path to save thumbnail pictures|str
|illust_cache_path|path to save large images(please manully delete cache)|str
|download_path|path to save orignal images|str
|auth_head_path|path to save author's head pictures|str

### Proxy
I use socks5 proxy, so if you are same with me it will be fine. 
For http proxy, I think change 

    proxies = {  
	    'https': 'socks5://127.0.0.1:1080',  
	    'http': 'socks5://127.0.0.1:1080'  
    }
   to
   
    proxies = {  
	    'https': 'http://127.0.0.1:1080',  
	    'http': 'http://127.0.0.1:1080'  
    }
can be okay(Maybe I guess:P)

## HOW TO USE IT 

 -  #### run `download_thbnl.py`
 -  #### when it done, run`Pixiv_Assistanec.py`

## What else should I write?
I think it's all :)