#coding:utf-8

"""
爬取 keras中文文档内容到本地.

@author: NosenLiu
 
@param root_url: keras中文文档url
@param root_dir: 网站内容存放地址
@param page_name: 本地静态网页名称
"""

from selenium import webdriver  #导入Selenium
import requests
from bs4 import BeautifulSoup  #导入BeautifulSoup 模块
import os  #导入os模块
import time
import urllib

root_url = "http://keras-cn.readthedocs.io/en/latest/"
root_dir = './latest/'
page_name = 'info.html'


# 下载器  这里的url必须是纯净的url，即没有tag的
def downloader(driver, url):  
    driver.get(url)   
    return driver

# TODO 用以搞定相对路径../ ./ 等问题
# TODO 出来的url类似http://keras-cn.readthedocs.io/en/latest/for_beginners/FAQ/
# TODO 该url对应的静态路径是 ./latest/for_beginners/FAQ
def get_abs_url(url,href):     
    if '../' in href:
        count = 0
        while('../' in href):
            count += 1
            href = href[3:]
        for i in range(count):
            if url[-1]=='/':     # 去除掉url最后一个 '/'
                url = url[:-1]
            rare = url.split('/')[-1]
            url = url.split(rare)[0]
        if href[-1]=='/':
            return url+href[:-1]
        else:
            return url+href
    elif './' in href:             
        href = href[2:]
        if url[-1]=='/':
            if href[-1]=='/':
                return url+href[:-1]
            else:
                return url+href
        else:
            if href[-1]=='/':
                return url+'/'+href[:-1]
            else:
                return url+'/'+href
    else:
        if url[-1]=='/':
            out_url = url+href
        else:
            out_url = url+'/'+href
        if out_url[-1]=='/':
            return out_url[:-1]
        else:
            return out_url

def save_data(driver, path):   # 这个path是指/latest/路径之后的path。 页面的话要加上  路径/info.html
    if path[-4:]=='.ico':
        with open('./latest/'+path,'wb') as f_in:
            f_in.write(driver.page_source)
    elif path[-4:]=='.css' or path[-3:]=='.js':
        with open('./latest/'+path,'wb') as f_in:
            f_in.write(driver.page_source.encode('utf-8'))
    else:
        with open('./latest/'+path+'/info.html','wb') as f_in:
            f_in.write(driver.page_source.encode('utf-8'))

def save_page(driver,save_path):
    with open(save_path+page_name,'wb') as f_in:
        f_in.write(driver.page_source.encode('utf-8'))
    temp_file_lines = []
    # 下面这一步把页面中的 'layers/pooling_layer/' 改为 './layers/pooling_layer/info.html'  以方便静态调用
    with open(save_path+page_name,'r', encoding="utf-8") as f_in:   
        f_lines = f_in.readlines()
        for i in range(len(f_lines)):
            if 'toctree-l1' in f_lines[i] and "href=\".\"" not in f_lines[i+1]:
                temp_loc = f_lines[i+1].split('"')[3]
                new_loc = './'+temp_loc+page_name
                f_lines[i+1] = f_lines[i+1].split(temp_loc)[0] + new_loc + f_lines[i+1].split(temp_loc)[1]
            temp_file_lines.append(f_lines[i].encode('utf-8'))  
    with open(save_path+page_name,'wb') as f_in:
        f_in.writelines(temp_file_lines)

def get_save_path(url):     # 将url变为相对的文件保存路径。
    if url[-1]!='/':
        url = url+'/'
    rare = url.split(root_url)[1]
    path = root_dir+rare
    return path


def main():
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    driver = webdriver.PhantomJS()
    driver.get(root_url)
    li_list = BeautifulSoup(driver.page_source,'html.parser').find_all('li',class_='toctree-l1')
    url_list = []      # 存取左侧目录中需要爬取的url
    for li in li_list:
        url_list.append(li.find('a')['href'])
    url_list = url_list[1:]
    for i in range(len(url_list)):
        url_list[i] = get_abs_url(root_url,url_list[i])    # 将真实(非相对路径) url进行替换。
    # for url in url_list:
    #     print(url)

    # TODO 在head标签中寻找 .css 及 .js
    link_list = BeautifulSoup(driver.page_source,'html.parser').find('head').find_all('link')
    script_list = BeautifulSoup(driver.page_source,'html.parser').find('head').find_all('script')
    css_list = []   # 存储css文件
    for link in link_list:
        href = link['href']
        if 'https://' in href:
            css_list.append(href)
        else:
            css_list.append(get_abs_url(root_url,href))
    js_list = []    # 存储 js 文件
    for js in script_list:
        try:
            href = js['src']
        except:
            continue
        if 'https://' in href:
            js_list.append(href)
        else:
            js_list.append(get_abs_url(root_url,href))

    # TODO 存储 /latest/info.html
    save_path = get_save_path(root_url)
    save_page(driver,save_path)
    
    # TODO   存储 css 和 js
    if not os.path.exists(root_dir+'css/'):
        os.makedirs(root_dir+'css/')
    for css in css_list:
        if root_url in css:
            save_path = get_save_path(css)[:-1]
        else:
            save_path = root_dir+'css/'+css
        try:
            driver.get(css)
            with open(save_path,'wb') as f_in:
                f_in.write(driver.page_source.encode('utf-8'))
        except:
            continue
    if not os.path.exists(root_dir+'js/'):
        os.makedirs(root_dir+'js/')
    for js in js_list:
        if root_url in js:
            save_path = get_save_path(js)[:-1]
        else:
            save_path = root_dir+'js/'+js
        try:
            driver.get(js)
            with open(save_path,'wb') as f_in:
                f_in.write(driver.page_source.encode('utf-8'))
        except:
            continue
  
    
    # 'http://keras-cn.readthedocs.io/en/latest/other/metrics' 
    # url_list中是类似地址， 先确定存储路径，创建文件夹路径，存储html文件，之后修改其中的href='XXXX/info.html'
    # TODO 现在开始 爬取 url_list 中的 41 个url
    for i in range(len(url_list)):
        time.sleep(3)  # 勿频繁访问，以防网站封禁
        save_path = get_save_path(url_list[i])
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        driver.get(url_list[i])
        save_page(driver,save_path)



if __name__ == '__main__':
    main()




