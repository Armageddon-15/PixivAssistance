
# 如何使用 PIXIV ASSISTANCE

## 做这个的原因
- 我很喜欢看二次元图片
- pixiv是我熟悉的网站
- 移动端代理不稳定（现在发现是pixiv的服务器不稳定，但还是比app稳）
- 用网页存图片很麻烦

## 简介
- 唯一目的就是更方便的储存pixiv的图片和gif


## 特点
- 简化储存操作，更快速储存组图和单图
- 可以储存gif
- 可以按tag分类储存图片


## GUI
- ### 探索界面 / Explore Widget
    探索界面目前基本上只能浏览关注的作者的更新的缩略图，你可以“喜欢”或者”喜欢并下载“. (我的习惯是喜欢所有想下载的图片) 。

    可以右键缩略图，有一些快捷操作：

    1. To Browser 打开当前illust所在的pixiv网页
    2. Update 更新数据，可以在 `save from id GUI.py` 之后用
    3. Locate Saved Path 打开储存的图片位置（第一次打开可能因为文件浏览器要更新缩略图所以定位不到，再定位一遍就好了）
   
    鼠标中键可以拖拽缩略图，里面有文本格式的 illust id


- ### 详情界面 / Detail Widget
   详情界面可以展示你在探索界面选择图片的预览或者gif原图、作者昵称、标签、和作品介绍。
   
   上面有作品标题，如果你想评论点一下就能去网页版。

   tag也可以点，会到网页版搜索tag

   鼠标移动到左右可以选择相邻的作品
   
   现在还不会自动加载，所以变量那里你可以更改每次加载数，按'N'加载.
   
   另外在这个界面里下载图片不会喜欢这个作品

- ### 其他
    界面右下角有donwload state 可以看到已储存的图片数/已储存+正在储存的图片数


## 下载
- 在探索界面“喜欢并下载” 会下载一个作品的所有图片和gif. 

- 在详情界面点击图片右下方按钮"↓"或者双击图片就可以下载这一张。

<br/>

# 如何使用 SAVE FROM ID GUI

## 功能
- 输入 illust id 和要储存的图片序号就可以储存对应的图片

- 可以拖拽网页端、PA的缩略图或者下载的图片文件/组图文件夹，会自动填充 illust id

- 最底下add就是新增一个下载模块，每次下载完就会自我销毁

## 一些没想好的地方
- 不知道怎么提示下载失败的原因所以只是save按钮变亮。
- 要是一个模块长时间下载没有消失，鼠标放在模块上面按enter就会重新下载

<br/>

# 声明
这是极早期版本，我也不怎么会编程，所以不论什么样的建议都可以给我说

<br/>

# 配置步骤
## 下载代码
|文件名| 用途 |
|--|--|
| `Detail_Widget.py` | `Pixiv_Assistance.py` 组件GUI |
| `Explore_Widget.py` | `Pixiv_Assistance.py` 组件GUI |
| `Pixiv_Assistance.py` | GUI |
|`save from id GUI.py`|第二个GUI，可以下载单独的illust|
|`save from id.py`|`save from id GUI.py` 前身，没有GUI的版本|
|`OpenFileFolder.py`|打开有特殊 tag 的 illust 所在文件夹的GUI|
|`download_thbnl.py` |更新关注作者的新作|
|`loop_upate.py`|循环更新关注作者的新作|
|`Illust.py`|`Illust` 类和方法文件，是核心|
|`Parameter.py`|参数设置|
|`reqiurements.txt`|配置工程用|
|`Refresh_token.py`|第一次登录用|
|`login_token`|存 refresh token 的。打开 `Refresh_token.py` 然后看 [跟着这个配置](https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362)|
|`special_tags.config`|会按照这个创建对应tag的文件夹，冒号左边是文件夹名，右边是tag。 <br/>空格分 tag 换行分文件夹名|
|<center>**文件夹名**</center>||
|`pixivpy3\`|pixivpy3的包，不想下可以pip|
|`notebook\`|pixivpy3带的，没用过|
|`venv\`|pycharm的虚拟环境，里面有一些包，不想下可以pip|
|`icon\`|图标|
|`data\`|存放illust数据的|
|`thumbnail\`|存放缩略图的|
|`cache\`|存放大一点的缩略图的|

如果你用pycharm，并且是py3.8，而且不想pip， 可以多下个文件夹`venv`，新建工程把`venv\Lib\site_package\`的文件放到相应位置

## 参数

在`Parameter.py`中设置
 
可以参照下面的表格

|参数名|用途|数据类型|
|--|--|--|
|utc_offset|时区偏移|int
|data_extension|保存数据的后缀|str
||<center>**路径**</center>|
|login_token|login_token的位置|str
|illust_data_path|保存数据的位置|str
|illust_thbnl_path|保存缩略图的位置|str
|illust_cache_path|保存大一点图片的位置(请手动删除)|str
|auth_head_path|保存作者头像的位置|str
|download_path|保存原图的位置|str
|r18_subfolder|r18的子文件夹，`""`就不会有新文件夹|str
||<center>**下载设置**</center>|
|max_download_thread|最大下载线程数|int
||<center>**详情界面**</center>|
|tag_pre_line|每行标签数|int
|stream_per_load|每次加载的图片数|int
||<center>**探索界面**</center>|
|like_btn_size| 按钮的大小|int
|thumbnail_size|缩略图大小|int
|pic_grid_row|乘以 pic_grid_column = 每页缩略图数|int
|pic_grid_column|乘以 pic_grid_row = 每页缩略图数|int
|nsfw|all-正常与R-18都有 sfw-只有正常 nsfw-只有R-18|int
||<center>**代理**</center>|
|proxy|代理设置|dict

### `Refresh_token.py` 的用法（如果你不想看链接）

1. 在terminal输入：

       python Refresh_token.py login
    
     - 如果发现在虚拟环境中安装了某个包却报错没有装用这行代码（我是这样的）
     
           venv\Scripts\python.exe Refresh_token.py login
    
       原因是pycharm terminal的python指向有问题
    
    这时会跳转到浏览器，pixiv登录的界面
   
2.  浏览器界面：

    1. 按 `F12`选择网页页面
    
    2. 勾选保留日志
    
    3. 正常登录
    
    4. 在日志中形如此`https://app-api.pixiv.net/web/v1/users/auth/pixiv/callback?state=...&code=...`的代码，把`code=`后的代码复制到terminal `code:`的后面
    
        - 但在我编辑readme时重新操作的过程中日志没有出现上述代码，反而在控制台报错区出现`Failed to launch 'pixiv://account/login?code="---我的code---"=login' because the scheme does not have a registered handler.`
       
 3. 在terminal按回车会出现`access_token`和`refresh_token`，把`refresh_token`后的内容复制到`login_token`即可


### 代理
我用的socks5代理，所以和我一样应该没什么问题

http代理的话，我觉得把

    proxies = {  
	    'https': 'socks5://127.0.0.1:1080',  
	    'http': 'socks5://127.0.0.1:1080'  
    }
  
  改成
   
    proxies = {  
	    'https': 'http://127.0.0.1:1080',  
	    'http': 'http://127.0.0.1:1080'  
    }
就好了（大概？）

## 怎么用呢

 1. 修改`Parameter.py`的变量
 
 2. 运行`download_thbnl.py`
 
 3. 运行`Pixiv_Assistanec.py`

## 想增加的功能
- 下载管理，更方便地查看下载进度
- 作者界面，更方便地下载作者作品
- 快捷键，总按鼠标手会疼

## 还写点啥?
就这样吧 :)
